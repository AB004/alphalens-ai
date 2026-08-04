# API Design

## Overview

AlphaLens exposes a REST API built with FastAPI.

The API is organized into modular services that mirror the system architecture.

Current API modules:

- Document Management
- PDF Processing
- RAG Indexing
- Document Intelligence
- Recommendation Engine
- Multi-Document Chat
- Conversation Management

Future modules:

- Authentication
- Market Intelligence
- Company Chat
- Long-Term Memory

All endpoints are prefixed with:

```text
/api
```

---

# Current API (Sprint 1)

---

# Document Management

## Upload PDFs

```http
POST /api/documents/upload
```

Upload one or more PDF files.

### Features

- Multiple PDF upload
- PDF validation
- Duplicate detection
- Persistent storage

---

## List Documents

```http
GET /api/documents
```

Returns uploaded documents.

---

## Get Document

```http
GET /api/documents/{document_id}
```

Returns document metadata.

---

## Delete Document

```http
DELETE /api/documents/{document_id}
```

Deletes:

- PDF
- Document metadata
- Chunk metadata
- FAISS index
- AI reports
- Recommendations

---

# PDF Processing

## Process Document

```http
POST /api/documents/{document_id}/process
```

Processes an uploaded PDF.

### Operations

- Text extraction
- Text cleaning
- Table detection
- Database persistence

---

## Get Processing Status

```http
GET /api/documents/{document_id}/status
```

Returns document processing status.

Possible values:

- uploaded
- processed
- indexed

---

# RAG Indexing

## Create Index

```http
POST /api/documents/{document_id}/index
```

Creates a FAISS index for semantic retrieval.

---

## Search Document

```http
POST /api/documents/{document_id}/search
```

Performs semantic search within a document.

Example

```json
{
    "query": "Revenue growth",
    "top_k": 5
}
```

---

# Document Intelligence

## Generate AI Report

```http
POST /api/documents/{document_id}/analysis
```

Generates:

- Executive Summary
- Financial Metrics
- SWOT Analysis
- Risk Analysis
- Opportunity Analysis

---

## Get AI Report

```http
GET /api/documents/{document_id}/analysis
```

Returns the stored AI-generated report.

---

# Recommendation Engine

## Generate Recommendation

```http
POST /api/documents/{document_id}/recommendation
```

Returns:

- Buy / Hold / Sell
- Confidence score
- Financial reasoning
- Supporting evidence

---

## Get Recommendation

```http
GET /api/documents/{document_id}/recommendation
```

Returns the stored recommendation.

---

# Multi-Document Chat

## Chat with Documents

```http
POST /api/documents/chat
```

Chat using one or multiple indexed documents.

Request

```json
{
    "document_ids": [1,2],
    "question": "Compare revenue growth."
}
```

Features:

- Single-document retrieval
- Multi-document retrieval
- Citation-aware responses
- Cross-document comparison

---

# Conversation Management

## Create Conversation

```http
POST /api/chat/sessions
```

Creates a persistent conversation.

Request

```json
{
    "title": "Reliance Analysis",
    "document_ids": [1]
}
```

---

## List Conversations

```http
GET /api/chat/sessions
```

Returns all conversations.

---

## Get Conversation

```http
GET /api/chat/sessions/{session_id}
```

Returns conversation metadata.

---

## Delete Conversation

```http
DELETE /api/chat/sessions/{session_id}
```

Deletes a conversation together with all stored messages.

---

## Send Message

```http
POST /api/chat/sessions/{session_id}/messages
```

Processes a conversational query using:

- Conversation history
- Retrieved document chunks
- Prompt builder
- Gemini

Example

```json
{
    "question": "What was last year's revenue?"
}
```

---

## Get Conversation Messages

```http
GET /api/chat/sessions/{session_id}/messages
```

Returns complete conversation history.

---

# End-to-End Request Flow

```text
User Request

      │

Conversation Lookup

      │

Recent Message Retrieval

      │

Document Retrieval (FAISS)

      │

Context Builder

      │

Prompt Generation

      │

Gemini

      │

Assistant Response

      │

Store User Message

      │

Store Assistant Message

      │

Return Response
```

---

# Planned APIs (Sprint 2)

The following APIs are planned for future releases.

---

## Company Intelligence

```http
GET /api/market/company/{symbol}
```

Returns company profile and financial information.

---

## Financial Statements

```http
GET /api/market/company/{symbol}/financials
```

---

## Financial Ratios

```http
GET /api/market/company/{symbol}/ratios
```

---

## Company News

```http
GET /api/market/company/{symbol}/news
```

---

## Sentiment Analysis

```http
GET /api/market/company/{symbol}/sentiment
```

---

## Market Recommendation

```http
GET /api/market/company/{symbol}/recommendation
```

---

## Company Chat

```http
POST /api/company/chat
```

Combines:

- Financial statements
- Market news
- Sentiment
- Conversation memory

---

# Planned APIs (Future)

## Authentication

```http
POST /api/auth/register
POST /api/auth/login
GET  /api/auth/me
```

---

## Advanced Conversation Memory

```http
GET    /api/memory/search
POST   /api/memory/summarize/{conversation_id}
DELETE /api/memory/{memory_id}
```

These APIs will support:

- Conversation summarization
- Semantic memory
- Cross-session retrieval

---

# API Design Principles

The AlphaLens API follows these principles:

- RESTful resource design
- Stateless request handling
- Persistent conversation history
- Modular service boundaries
- Explainable AI responses with citations
- Separation of document intelligence and market intelligence
- Extensible architecture for future AI capabilities