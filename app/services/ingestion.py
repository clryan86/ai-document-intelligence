from __future__ import annotations

import hashlib
from pathlib import Path

from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import Chunk, Document
from .extraction import extract_text
from .nlp import chunk_text


class DuplicateDocumentError(ValueError):
    def __init__(self, existing_id: int):
        self.existing_id = existing_id
        super().__init__(f"Document already exists with id={existing_id}")


def safe_filename(filename: str) -> str:
    clean = Path(filename or "document.txt").name.replace("\x00", "").strip()
    return clean or "document.txt"


def ingest_document(session: Session, storage_dir: Path, filename: str, content_type: str, payload: bytes) -> Document:
    digest = hashlib.sha256(payload).hexdigest()
    existing = session.scalar(select(Document).where(Document.sha256 == digest))
    if existing:
        raise DuplicateDocumentError(existing.id)

    clean_name = safe_filename(filename)
    text = extract_text(clean_name, payload)
    document = Document(filename=clean_name,content_type=content_type or "application/octet-stream",sha256=digest,byte_size=len(payload),text_content=text)
    session.add(document)
    session.flush()
    for position, chunk in enumerate(chunk_text(text)):
        session.add(Chunk(document_id=document.id, position=position, text=chunk))
    storage_dir.mkdir(parents=True, exist_ok=True)
    stored_path = storage_dir / f"{digest[:16]}_{clean_name}"
    stored_path.write_bytes(payload)
    session.commit()
    session.refresh(document)
    return document
