from pathlib import Path

from fastapi.testclient import TestClient

from app.config import Settings
from app.main import create_app


def build_client(tmp_path: Path) -> TestClient:
    settings = Settings(database_url=f"sqlite:///{(tmp_path / 'test.db').as_posix()}",storage_dir=tmp_path / "uploads",max_upload_bytes=1024 * 1024)
    return TestClient(create_app(settings))

def test_healthz(tmp_path):
    client=build_client(tmp_path); response=client.get("/healthz"); assert response.status_code==200; assert response.json()["ok"] is True

def test_upload_search_intelligence_and_delete_flow(tmp_path):
    client=build_client(tmp_path)
    payload=(b"Python automation helps teams reduce repetitive work. " b"FastAPI provides typed APIs. Testing and CI improve reliability. " b"SQL databases preserve operational records.")
    created=client.post("/api/documents",files={"file":("automation.txt",payload,"text/plain")}); assert created.status_code==201
    document_id=created.json()["id"]; assert created.json()["word_count"]>10
    listed=client.get("/api/documents"); assert listed.status_code==200; assert listed.json()[0]["filename"]=="automation.txt"
    intelligence=client.get(f"/api/documents/{document_id}/intelligence"); assert intelligence.status_code==200; assert "python" in intelligence.json()["keywords"]
    search=client.get("/api/search",params={"q":"FastAPI automation"}); assert search.status_code==200; assert search.json()["total_hits"]>=1
    analytics=client.get("/api/analytics"); assert analytics.status_code==200; assert analytics.json()["documents"]==1
    deleted=client.delete(f"/api/documents/{document_id}"); assert deleted.status_code==204
    assert client.get(f"/api/documents/{document_id}").status_code==404

def test_duplicate_document_returns_conflict(tmp_path):
    client=build_client(tmp_path); payload=b"duplicate document content for deterministic hashing"
    assert client.post("/api/documents",files={"file":("one.txt",payload,"text/plain")}).status_code==201
    assert client.post("/api/documents",files={"file":("two.txt",payload,"text/plain")}).status_code==409
