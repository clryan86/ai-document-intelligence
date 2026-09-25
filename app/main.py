from __future__ import annotations

from pathlib import Path

from fastapi import Depends, FastAPI, File, HTTPException, Query, Request, UploadFile
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from sqlalchemy import func, select
from sqlalchemy.orm import Session, selectinload

from .config import Settings
from .database import Base, build_engine, build_session_factory
from .models import Chunk, Document
from .schemas import AnalyticsResponse, DocumentDetail, DocumentSummary, IntelligenceResponse, SearchHit, SearchResponse
from .services.ingestion import DuplicateDocumentError, ingest_document
from .services.nlp import extract_keywords, semantic_search, summarize

ROOT = Path(__file__).resolve().parents[1]
TEMPLATES = Jinja2Templates(directory=str(ROOT / "templates"))


def create_app(settings: Settings | None = None) -> FastAPI:
    settings = settings or Settings.from_env()
    settings.storage_dir.mkdir(parents=True, exist_ok=True)
    engine = build_engine(settings.database_url)
    session_factory = build_session_factory(engine)
    Base.metadata.create_all(engine)

    app = FastAPI(
        title=settings.app_name,
        version="1.0.0",
        description="A portfolio-grade document ingestion, search, and NLP intelligence service.",
    )
    app.state.settings = settings
    app.state.engine = engine
    app.state.session_factory = session_factory

    app.mount("/static", StaticFiles(directory=str(ROOT / "static")), name="static")

    def get_session(request: Request):
        session = request.app.state.session_factory()
        try:
            yield session
        finally:
            session.close()

    @app.get("/healthz")
    def healthz():
        return {"ok": True, "service": settings.app_name}

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request, session: Session = Depends(get_session)):
        documents = session.scalars(select(Document).order_by(Document.created_at.desc())).all()
        return TEMPLATES.TemplateResponse(
            request=request,
            name="index.html",
            context={"documents": documents, "app_name": settings.app_name},
        )

    @app.post("/upload")
    async def browser_upload(request: Request, file: UploadFile = File(...), session: Session = Depends(get_session)):
        payload = await file.read(settings.max_upload_bytes + 1)
        if len(payload) > settings.max_upload_bytes:
            return RedirectResponse(url="/?error=file-too-large", status_code=303)
        try:
            document = ingest_document(
                session,
                settings.storage_dir,
                file.filename or "document",
                file.content_type or "application/octet-stream",
                payload,
            )
        except DuplicateDocumentError as exc:
            return RedirectResponse(url=f"/documents/{exc.existing_id}", status_code=303)
        except ValueError:
            return RedirectResponse(url="/?error=unsupported-or-empty", status_code=303)
        return RedirectResponse(url=f"/documents/{document.id}", status_code=303)

    @app.get("/documents/{document_id}", response_class=HTMLResponse)
    def document_page(document_id: int, request: Request, session: Session = Depends(get_session)):
        document = session.scalar(
            select(Document).options(selectinload(Document.chunks)).where(Document.id == document_id)
        )
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        intelligence = {
            "summary": summarize(document.text_content),
            "keywords": extract_keywords(document.text_content),
        }
        return TEMPLATES.TemplateResponse(
            request=request,
            name="document.html",
            context={"document": document, "intelligence": intelligence, "app_name": settings.app_name},
        )

    @app.get("/search", response_class=HTMLResponse)
    def browser_search(request: Request, q: str = Query(default=""), session: Session = Depends(get_session)):
        hits = _search(session, q, limit=12)
        return TEMPLATES.TemplateResponse(
            request=request,
            name="search.html",
            context={"query": q, "hits": hits, "app_name": settings.app_name},
        )

    @app.post("/api/documents", response_model=DocumentDetail, status_code=201)
    async def api_upload(file: UploadFile = File(...), session: Session = Depends(get_session)):
        payload = await file.read(settings.max_upload_bytes + 1)
        if len(payload) > settings.max_upload_bytes:
            raise HTTPException(status_code=413, detail="File exceeds upload limit")
        try:
            document = ingest_document(
                session,
                settings.storage_dir,
                file.filename or "document",
                file.content_type or "application/octet-stream",
                payload,
            )
        except DuplicateDocumentError as exc:
            raise HTTPException(status_code=409, detail={"message": "Duplicate document", "document_id": exc.existing_id})
        except ValueError as exc:
            raise HTTPException(status_code=422, detail=str(exc))
        return _document_detail(document)

    @app.get("/api/documents", response_model=list[DocumentSummary])
    def api_documents(session: Session = Depends(get_session)):
        documents = session.scalars(
            select(Document).options(selectinload(Document.chunks)).order_by(Document.created_at.desc())
        ).all()
        return [_document_summary(d) for d in documents]

    @app.get("/api/documents/{document_id}", response_model=DocumentDetail)
    def api_document(document_id: int, session: Session = Depends(get_session)):
        document = session.scalar(
            select(Document).options(selectinload(Document.chunks)).where(Document.id == document_id)
        )
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return _document_detail(document)

    @app.get("/api/documents/{document_id}/intelligence", response_model=IntelligenceResponse)
    def api_intelligence(document_id: int, session: Session = Depends(get_session)):
        document = session.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        return IntelligenceResponse(
            document_id=document.id,
            summary=summarize(document.text_content),
            keywords=extract_keywords(document.text_content),
        )

    @app.delete("/api/documents/{document_id}", status_code=204)
    def api_delete_document(document_id: int, session: Session = Depends(get_session)):
        document = session.get(Document, document_id)
        if not document:
            raise HTTPException(status_code=404, detail="Document not found")
        session.delete(document)
        session.commit()
        return None

    @app.get("/api/search", response_model=SearchResponse)
    def api_search(q: str = Query(min_length=2), limit: int = Query(default=8, ge=1, le=25), session: Session = Depends(get_session)):
        hits = _search(session, q, limit)
        return SearchResponse(query=q, total_hits=len(hits), hits=hits)

    @app.get("/api/analytics", response_model=AnalyticsResponse)
    def api_analytics(session: Session = Depends(get_session)):
        document_count = session.scalar(select(func.count(Document.id))) or 0
        chunk_count = session.scalar(select(func.count(Chunk.id))) or 0
        total_bytes = session.scalar(select(func.coalesce(func.sum(Document.byte_size), 0))) or 0
        documents = session.scalars(select(Document.text_content)).all()
        total_words = sum(len(text.split()) for text in documents)
        return AnalyticsResponse(
            documents=int(document_count),
            chunks=int(chunk_count),
            total_bytes=int(total_bytes),
            total_words=int(total_words),
        )

    return app


def _document_summary(document: Document) -> DocumentSummary:
    return DocumentSummary(
        id=document.id,
        filename=document.filename,
        content_type=document.content_type,
        byte_size=document.byte_size,
        created_at=document.created_at,
        chunk_count=len(document.chunks),
    )


def _document_detail(document: Document) -> DocumentDetail:
    return DocumentDetail(
        **_document_summary(document).model_dump(),
        character_count=len(document.text_content),
        word_count=len(document.text_content.split()),
        preview=document.text_content[:1200],
    )


def _search(session: Session, query: str, limit: int) -> list[SearchHit]:
    rows = session.execute(
        select(Chunk, Document).join(Document, Chunk.document_id == Document.id).order_by(Document.id, Chunk.position)
    ).all()
    chunks = [chunk.text for chunk, _ in rows]
    ranked = semantic_search(query, chunks, limit=limit)
    hits: list[SearchHit] = []
    for index, score in ranked:
        chunk, document = rows[index]
        hits.append(
            SearchHit(
                document_id=document.id,
                filename=document.filename,
                chunk_id=chunk.id,
                position=chunk.position,
                score=round(score, 4),
                text=chunk.text[:700],
            )
        )
    return hits


app = create_app()
