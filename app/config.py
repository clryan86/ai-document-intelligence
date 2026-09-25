from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class Settings:
    database_url: str
    storage_dir: Path
    max_upload_bytes: int = 5 * 1024 * 1024
    app_name: str = "Document Intelligence Workbench"

    @classmethod
    def from_env(cls) -> "Settings":
        root = Path(__file__).resolve().parents[1]
        storage = Path(os.getenv("STORAGE_DIR", root / "data" / "uploads"))
        database_url = os.getenv(
            "DATABASE_URL",
            f"sqlite:///{(root / 'data' / 'document_intelligence.db').as_posix()}",
        )
        max_mb = int(os.getenv("MAX_UPLOAD_MB", "5"))
        return cls(
            database_url=database_url,
            storage_dir=storage,
            max_upload_bytes=max_mb * 1024 * 1024,
        )
