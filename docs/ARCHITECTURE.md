# AlphaLens Architecture

## Overview

AlphaLens contains two products that share a FastAPI backend and persistent
storage: Financial Document Intelligence and Market Intelligence.

## Financial Document Pipeline (Modules 1 and 2)

```text
PDF upload
  -> validate filename, PDF signature, size, and readability
  -> store the PDF in backend/uploads
  -> persist document metadata in SQLite (or DATABASE_URL)
  -> extract text with pypdf
  -> clean text and detect text-layout tables
  -> persist processing result and status
```

The database is the source of truth for document IDs and processing state.
Files are stored on disk and are removed together with their database record.

Module 3 will add chunking, embeddings, and FAISS on top of the persisted
clean-text records.

## Shared Components

- FastAPI API layer
- SQLAlchemy persistence layer
- SQLite during local development; configurable database URL for deployment
- File storage for uploaded PDFs
- Future AI layer: embeddings, FAISS, prompts, and LLM integration
