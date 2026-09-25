# Interview Guide

This file is for explaining the project clearly in an interview. Do not memorize it word-for-word; understand the decisions well enough to discuss them naturally.

## 30-second overview

> Document Intelligence Workbench is a FastAPI application that ingests PDF, Markdown, and text files, extracts and stores their content, breaks documents into searchable chunks, and provides local NLP features such as ranked passage search, extractive summaries, and keyword extraction. I designed it so a reviewer can run everything without a paid AI API, while keeping the NLP layer modular enough to swap in embeddings or an LLM later.

## Problem it solves

Teams often have useful information trapped in unstructured documents. The project demonstrates the core pipeline behind a lightweight internal knowledge system:

1. validate and ingest files,
2. extract text,
3. normalize and chunk content,
4. persist document/chunk data,
5. retrieve relevant passages,
6. generate useful document-level intelligence,
7. expose it through both a UI and API.

## Architecture talking points

### Why FastAPI?

- typed request/response contracts
- built-in validation
- automatic OpenAPI documentation
- strong fit for service-oriented Python backends
- easy testing through ASGI TestClient

### Why SQLAlchemy?

- explicit relational model
- clean separation from SQLite
- straightforward path to PostgreSQL
- document/chunk relationship models a real retrieval pipeline

### Why TF-IDF instead of calling an LLM?

The baseline needed to be reproducible, free to run, deterministic, and testable in CI. TF-IDF provides a transparent retrieval baseline. The NLP service boundary makes it possible to add embeddings or an LLM without rewriting ingestion, persistence, routes, or the UI.

### Why chunk documents?

Searching an entire document can hide the relevant section. Passage-level chunks improve precision and also map naturally to a future vector-search architecture.

### How does deduplication work?

The uploaded bytes are hashed with SHA-256. The hash is unique in the document table. A second upload of identical bytes returns a conflict instead of creating duplicate corpus data.

### What would you change for production?

- authentication and authorization
- PostgreSQL
- object storage instead of local files
- malware scanning
- rate limiting
- asynchronous ingestion workers
- proper migrations
- structured logs and metrics
- embeddings/vector index for larger corpora
- tenant/workspace isolation
- backup and data-retention policies

## Technical questions you should be ready for

**What happens when a document is uploaded?**  
FastAPI validates the request, reads a bounded payload, hashes it, checks for duplicates, extracts text based on extension, chunks the text, writes document/chunk rows through SQLAlchemy, stores the original payload, and commits the transaction.

**How does search work?**  
The system vectorizes the query and stored chunks with a TF-IDF vectorizer using unigrams and bigrams, calculates cosine similarity, then returns the highest-scoring passages.

**What is the biggest scalability limitation?**  
Search currently rebuilds the TF-IDF matrix at query time. That is intentionally simple for a portfolio-sized corpus. At scale, I would precompute embeddings and use a vector database or indexed search engine.

**How is it tested?**  
Unit tests validate chunking, summarization, keywords, and retrieval ranking. API integration tests create a temporary database and exercise upload, listing, intelligence, search, analytics, duplicate detection, and deletion.

## Resume-style project bullets

- Built a FastAPI document-intelligence service supporting PDF/TXT/Markdown ingestion, normalized persistence, passage-level search, extractive summarization, and keyword extraction.
- Designed SQLAlchemy document/chunk models with SHA-256 deduplication and a migration path from SQLite to PostgreSQL/vector search.
- Added automated API/NLP tests, GitHub Actions CI, Docker deployment, OpenAPI documentation, and security/architecture documentation.
