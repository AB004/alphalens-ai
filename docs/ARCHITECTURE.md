# AlphaLens Architecture

## Overview

AlphaLens contains two products that share a FastAPI backend and persistent
storage: Financial Document Intelligence and Market Intelligence.

## Financial Document Pipeline (Modules 1–3)

```text
PDF upload
  -> validate filename, PDF signature, size, and readability
  -> store the PDF in backend/uploads
  -> persist document metadata in SQLite (or DATABASE_URL)
  -> extract text with pypdf
  -> clean text and detect text-layout tables
  -> persist processing result and status
  -> create page-aware chunks
  -> embed chunks with SentenceTransformer
  -> persist FAISS index and chunk/page metadata
  -> semantic search with page citations
```

The database is the source of truth for document IDs and processing state.
Files are stored on disk and are removed together with their database record.

Modules 1–3 form the persistent retrieval foundation for the document
intelligence modules that follow.

## Shared Components

- FastAPI API layer
- SQLAlchemy persistence layer
- SQLite during local development; configurable database URL for deployment
- File storage for uploaded PDFs
- Future AI layer: embeddings, FAISS, prompts, and LLM integration
