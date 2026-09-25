# Document Intelligence Workbench

[![CI](https://github.com/clryan86/ai-document-intelligence/actions/workflows/ci.yml/badge.svg)](https://github.com/clryan86/ai-document-intelligence/actions/workflows/ci.yml)
![Python](https://img.shields.io/badge/Python-3.11%2B-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-typed%20API-009688)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-2.x-red)
![Docker](https://img.shields.io/badge/Docker-ready-2496ED)
![License](https://img.shields.io/badge/license-MIT-green)

A full-stack document ingestion and retrieval application built to demonstrate **Python backend engineering, applied NLP, data modeling, API design, testing, CI, and containerized deployment**.

The system accepts PDF, Markdown, and text documents; extracts their content; breaks them into searchable passages; stores normalized data in SQLite; and provides summaries, keywords, ranked search results, analytics, a browser UI, and a typed REST API.

> **Portfolio focus:** This project is intentionally useful without a paid AI API. Its NLP baseline is deterministic and testable, while the architecture leaves a clean upgrade path to embeddings, a vector database, or an LLM provider.

## What this demonstrates

- FastAPI application architecture
- typed REST endpoints and OpenAPI docs
- SQLAlchemy 2.x relational modeling
- file ingestion and validation
- PDF/text extraction
- NLP retrieval using TF-IDF + cosine similarity
- extractive summarization
- keyword extraction
- SHA-256 deduplication
- automated API and unit tests
- Ruff linting
- GitHub Actions CI across multiple Python versions
- Docker / Docker Compose deployment
- recruiter-friendly technical documentation

## Product capabilities

### Document ingestion
- PDF, TXT, and Markdown support
- bounded upload size
- safe filename handling
- content hashing and duplicate detection
- persisted raw upload copy
- normalized text extraction

### Document intelligence
- chunked knowledge representation
- ranked passage search
- extractive summaries
- keyword extraction
- document-level metrics
- corpus analytics

### Interfaces
- responsive browser UI
- REST API under `/api`
- interactive Swagger/OpenAPI docs at `/docs`
- health endpoint at `/healthz`

## Architecture

```text
Browser/API ---> FastAPI
                  |
          -------------------
          |        |        |
       Extract    NLP    Persistence
       PDF/TXT   TF-IDF   SQLAlchemy
       Markdown  Summary  SQLite
                 Keywords
```

See [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md) for the full system design.

## Quick start

```bash
python -m venv .venv
# macOS/Linux: source .venv/bin/activate
# Windows PowerShell: .\.venv\Scripts\Activate.ps1
pip install -r requirements-dev.txt
uvicorn app.main:app --reload
```

Open the UI at `http://127.0.0.1:8000`, API docs at `/docs`, and health check at `/healthz`.

Load the included demo document with `python scripts/demo_seed.py`.

## Quality checks

```bash
pytest
ruff check .
```

## Docker

```bash
docker compose up --build
```

## Engineering decisions

The application uses deterministic local NLP so a reviewer can run and verify it without a private API key. Passage-level chunks improve retrieval and create a natural upgrade path for future vector embeddings. Original text and chunks are both stored so ingestion remains auditable and multiple downstream intelligence strategies can be added without repeatedly parsing the binary source.

## Roadmap

- optional embedding provider and vector index
- pluggable LLM summarization interface
- authentication and per-user workspaces
- PostgreSQL deployment profile
- asynchronous ingestion workers
- OCR for image-only PDFs
- observability and structured metrics

## Author

**Christopher Ryan**  
Python • Backend • Automation • Data & Applied AI

Built as part of a professional software-engineering portfolio focused on practical, testable, deployable systems.

## License

MIT
