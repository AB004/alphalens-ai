# API Design

## Overview

AlphaLens exposes a REST API built with FastAPI.

The API is organized into independent modules that mirror the system architecture:

- Authentication
- Document Management
- PDF Processing
- RAG & Retrieval
- Conversation Management
- Memory Management
- Document Intelligence
- Market Intelligence
- Recommendations

All application routes are prefixed with:

```text
/api
```

---

# Authentication

## Register

```http
POST /auth/register
```

Creates a new user account.

---

## Login

```http
POST /auth/login
```

Returns an authentication token.

---

## Get Current User

```http
GET /auth/me
```

Returns authenticated user information.

---

# Document Management

## Upload PDFs

```http
POST /documents/upload
```

Upload one or more PDF files.

### Features

- Multiple file upload
- PDF validation
- Duplicate detection
- Persistent storage

Response

```json
{
    "document_ids": [1,2,3]
}
```

---

## List Documents

```http
GET /documents
```

Returns all uploaded documents.

---

## Get Document

```http
GET /documents/{document_id}
```

Returns document metadata.

---

## Delete Document

```http
DELETE /documents/{document_id}
```

Deletes

- PDF
- Metadata
- Processed text
- FAISS index

---

# PDF Processing

## Process Documents

```http
POST /documents/process
```

Processes uploaded PDFs.

### Operations

- Text extraction
- Cleaning
- Table detection
- Database persistence

Request

```json
{
    "document_ids":[1,2]
}
```

---

## Get Processing Status

```http
GET /documents/{document_id}/status
```

Returns

- Uploaded
- Processing
- Processed
- Indexed

---

# RAG Indexing

## Create Index

```http
POST /documents/{document_id}/index
```

Creates a FAISS index.

Request

```json
{
    "chunk_size":1200,
    "chunk_overlap":200
}
```

---

## Search Document

```http
POST /documents/{document_id}/search
```

Semantic search within one document.

Request

```json
{
    "query":"Revenue growth",
    "top_k":5
}
```

Response

```json
{
    "results":[
        {
            "page":42,
            "score":0.91,
            "text":"..."
        }
    ]
}
```

---

## Search Multiple Documents

```http
POST /documents/search
```

Searches across multiple uploaded documents.

---

# Conversation Management

Unlike a traditional RAG application, AlphaLens stores conversations and supports long-term memory.

---

## Create Conversation

```http
POST /conversations
```

Creates a new conversation.

Response

```json
{
    "conversation_id":1
}
```

---

## List Conversations

```http
GET /conversations
```

Returns all conversations.

---

## Get Conversation

```http
GET /conversations/{conversation_id}
```

Returns conversation details.

---

## Conversation History

```http
GET /conversations/{conversation_id}/messages
```

Returns all messages.

---

## Delete Conversation

```http
DELETE /conversations/{conversation_id}
```

Deletes

- Messages
- Conversation summary
- Conversation memory

---

# Document Chat

## Chat with Documents

```http
POST /chat/document
```

Uses

- Recent conversation
- Conversation memory
- Retrieved document chunks

Request

```json
{
    "conversation_id":1,
    "document_ids":[1,2],
    "message":"Compare revenue growth."
}
```

Response

```json
{
    "response":"...",
    "citations":[
        {
            "document":1,
            "page":42
        }
    ]
}
```

---

# Company Chat

## Chat with Company

```http
POST /chat/company
```

Uses

- Financial statements
- News
- Sentiment
- Previous conversations

Request

```json
{
    "conversation_id":5,
    "symbol":"AAPL",
    "message":"Is the company financially healthy?"
}
```

---

# Memory API

The memory system enables ChatGPT-like conversations across multiple sessions.

---

## Search Memory

```http
GET /memory/search
```

Searches long-term conversation memories.

Example

```http
GET /memory/search?query=Tesla
```

---

## List Memories

```http
GET /memory
```

Returns stored memories.

---

## Generate Conversation Summary

```http
POST /memory/summarize/{conversation_id}
```

Creates or updates a conversation summary.

---

## Delete Memory

```http
DELETE /memory/{memory_id}
```

Deletes a stored memory.

---

# Document Intelligence

## Generate AI Report

```http
POST /documents/{document_id}/summary
```

Generates

- Executive summary
- SWOT
- Risks
- Opportunities

---

## Extract Financial Metrics

```http
POST /documents/{document_id}/metrics
```

Returns structured financial metrics with citations.

---

## Generate Recommendation

```http
POST /documents/{document_id}/recommendation
```

Returns

- Buy / Hold / Sell
- Confidence
- Supporting evidence

---

# Market Intelligence

## Search Company

```http
GET /market/company/{symbol}
```

Returns company profile.

---

## Financial Statements

```http
GET /market/company/{symbol}/financials
```

Returns financial statements.

---

## Financial Ratios

```http
GET /market/company/{symbol}/ratios
```

Returns calculated financial ratios.

---

## Company News

```http
GET /market/company/{symbol}/news
```

Returns aggregated news.

---

## Sentiment Analysis

```http
GET /market/company/{symbol}/sentiment
```

Returns

- Positive
- Neutral
- Negative
- Confidence

---

## Market Recommendation

```http
GET /market/company/{symbol}/recommendation
```

Returns

- Buy
- Hold
- Sell
- Explanation

---

# Health Check

```http
GET /health
```

Returns service health.

Example

```json
{
    "status":"healthy"
}
```

---

# End-to-End AI Request Flow

```text
User Request
      │
      ▼

Conversation Lookup

      │
      ▼

Recent Messages

      │
      ▼

Memory Retrieval

      │
      ▼

Document Retrieval

      │
      ▼

Market Retrieval
(optional)

      │
      ▼

Context Builder

      │
      ▼

Gemini API

      │
      ▼

Assistant Response

      │
      ▼

Save Conversation

      │
      ▼

Update Conversation Memory
```

---

# API Design Principles

The AlphaLens API follows these principles:

- RESTful resource design
- Stateless request handling
- Persistent conversation memory
- Modular service boundaries
- Explainable AI responses with citations
- Separation of document intelligence and market intelligence
- Extensible architecture for future agents and tools