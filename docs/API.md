# API Guide

Interactive OpenAPI documentation is available at `/docs` when the service is running.

| Method | Path | Purpose |
| --- | --- | --- |
| GET | `/healthz` | Service health check |
| POST | `/api/documents` | Upload and ingest a document |
| GET | `/api/documents` | List ingested documents |
| GET | `/api/documents/{id}` | Document metadata and preview |
| GET | `/api/documents/{id}/intelligence` | Summary and keywords |
| DELETE | `/api/documents/{id}` | Delete a document and its chunks |
| GET | `/api/search?q=...` | Rank relevant passages |
| GET | `/api/analytics` | Corpus totals |
