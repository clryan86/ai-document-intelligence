import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from app.config import Settings
from app.database import Base, build_engine, build_session_factory
from app.services.ingestion import DuplicateDocumentError, ingest_document

settings = Settings.from_env()
engine = build_engine(settings.database_url)
Base.metadata.create_all(engine)
Session = build_session_factory(engine)

sample = ROOT / "sample_docs" / "automation_strategy.md"
with Session() as session:
    try:
        document = ingest_document(session, settings.storage_dir, sample.name, "text/markdown", sample.read_bytes())
        print(f"Seeded document #{document.id}: {document.filename}")
    except DuplicateDocumentError as exc:
        print(f"Sample already exists as document #{exc.existing_id}")
