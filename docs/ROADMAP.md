# AlphaLens Roadmap

## Current foundation — complete

- Module 1: PDF upload, validation, file management, and persistent metadata
- Module 2: PDF text extraction, cleaning, table-layout detection, and
  persistent processing results
- Module 3: page-aware chunking, SentenceTransformer embeddings, persisted
  FAISS indexes, and semantic retrieval with source-page metadata

The foundation is verified against the 383-page Infosys annual report using
the complete upload → process → index → semantic search → delete API lifecycle.

## Sprint 1 — Financial Document Intelligence

### Module 4 — Document Intelligence

- Structured financial metric extraction with source citations
- Executive summary, risks, opportunities, and SWOT generation
- Stored report result for repeatable viewing

Milestone: Explainable AI research report for an uploaded company document.

### Module 5 — Financial Recommendation

- Transparent rules over extracted financial features
- Buy / Hold / Sell score, confidence, reasons, and cited evidence
- Explicit disclaimer that output is educational, not investment advice

### Module 6 — Multi-document Chat

- Retrieval, prompt building, and answer citations
- Single-document and multi-document chat
- Cross-company comparison with source/page references

Milestone: Complete Financial Document Intelligence workflow.

## Sprint 2 — Market Intelligence

### Modules 7–11

- Company search, statements, and ratios
- News collection, deduplication, and caching
- FinBERT sentiment aggregation
- Explainable market recommendation
- Company chat grounded in financial data and news

Milestone: Complete Market Intelligence workflow.

## Sprint 3 — Resume-ready production release

### Modules 12–14

- Next.js dashboard, upload, report, comparison, and chat interfaces
- API, integration, retrieval-quality, and sentiment-validation tests
- Docker, environment configuration, deployment, and observability
- README with architecture diagram, demo screenshots, API examples, and
  measurable evaluation results

Milestone: AlphaLens v1 — a deployed, demonstrable end-to-end portfolio project.
