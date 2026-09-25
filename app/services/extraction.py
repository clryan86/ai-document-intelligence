from __future__ import annotations

import io
from pathlib import Path

from pypdf import PdfReader


SUPPORTED_EXTENSIONS = {".txt", ".md", ".pdf"}


class UnsupportedDocumentError(ValueError):
    pass


def extract_text(filename: str, payload: bytes) -> str:
    suffix = Path(filename).suffix.lower()
    if suffix not in SUPPORTED_EXTENSIONS:
        raise UnsupportedDocumentError(
            f"Unsupported file type '{suffix or 'unknown'}'. Supported: .txt, .md, .pdf"
        )

    if suffix in {".txt", ".md"}:
        text = payload.decode("utf-8", errors="replace")
    else:
        reader = PdfReader(io.BytesIO(payload))
        text = "\n\n".join((page.extract_text() or "") for page in reader.pages)

    normalized = "\n".join(line.rstrip() for line in text.replace("\r\n", "\n").split("\n"))
    if not normalized.strip():
        raise ValueError("No readable text could be extracted from this document.")
    return normalized.strip()
