# AlphaLens Architecture

## Overview

AlphaLens is an AI Financial Research Assistant that combines document intelligence, Retrieval-Augmented Generation (RAG), persistent conversation memory, and explainable AI to analyze financial reports through natural conversations.

The architecture is modular and evolves incrementally across three sprints.

Current implementation focuses on Financial Document Intelligence, while Market Intelligence and advanced AI capabilities are planned for future releases.

---

# Current Architecture (Sprint 1)

The current system consists of four primary layers.

1. Document Processing
2. Retrieval-Augmented Generation (RAG)
3. Conversation & Context Management
4. AI Reasoning

---

# High-Level Architecture

```text
                            User
                              │
                              ▼

                        FastAPI Backend

                              │

      ┌───────────────────────┼────────────────────────┐
      ▼                       ▼                        ▼

 Document Processing      Conversation Layer      AI Reasoning

      │                       │                        │
      ▼                       ▼                        ▼

 PDF Upload          Conversation Sessions      Context Builder
 PDF Processing       Chat History              Prompt Builder
 Chunking             Message Storage                │
 Embeddings           Follow-up Memory              ▼
 FAISS Search              │                    Gemini API
      │                    ▼                        │
      └──────────────► Context ◄────────────────────┘
                              │
                              ▼
                     Assistant Response
                              │
                              ▼
                   Persist Conversation
```

---

# 1. Document Processing Layer

Responsible for transforming uploaded financial reports into searchable knowledge.

## Workflow

```text
PDF Upload

      │

Validation

      │

Text Extraction

      │

Cleaning

      │

Table Detection

      │

Database Storage

      │

Page-aware Chunking

      │

SentenceTransformer Embeddings

      │

FAISS Index
```

### Responsibilities

- Multiple PDF upload
- PDF validation
- Text extraction
- Table detection
- Text cleaning
- Page-aware chunking
- Embedding generation
- FAISS indexing

---

# 2. Retrieval-Augmented Generation (RAG)

Provides semantic retrieval over uploaded documents.

## Workflow

```text
User Question

      │

Sentence Embedding

      │

FAISS Similarity Search

      │

Relevant Chunks

      │

Context Builder
```

### Responsibilities

- Semantic document retrieval
- Page citation support
- Multi-document retrieval
- Cross-document comparison

---

# 3. Conversation & Context Management

Unlike traditional RAG applications, AlphaLens maintains persistent conversations.

Conversation history is stored in the relational database and reused for follow-up questions.

## Current Memory Architecture

```text
Conversation Session

        │

Chat Messages

(SQL Database)

        │

Recent Conversation

        │

Context Builder

        │

Gemini
```

### Current Features

- Persistent chat sessions
- Multi-turn conversations
- Follow-up question handling
- Conversation history retrieval
- Context-aware prompting

Conversation history is merged with retrieved document chunks before each LLM request.

---

# 4. AI Reasoning Layer

Every user request passes through a unified reasoning pipeline.

```text
User Question

        │

Retrieve Chat History

        │

Retrieve Document Chunks

        │

Merge Context

        │

Prompt Builder

        │

Gemini API

        │

Assistant Response

        │

Store Conversation
```

---

# Context Builder

The Context Builder combines multiple sources into a single prompt.

Current sources:

- Recent conversation history
- Retrieved document chunks
- User question

Future versions will additionally include:

- Company financial data
- Market news
- Sentiment analysis
- Long-term semantic memory

---

# Storage Architecture

## Relational Database

Stores structured application data.

Current tables include:

- Documents
- Document Chunks
- Document Indexes
- AI Reports
- Recommendations
- Conversation Sessions
- Chat Messages

---

## File Storage

Stores uploaded PDF files.

---

## FAISS Vector Storage

Stores document embeddings for semantic retrieval.

```text
Question

      │

Embedding

      │

FAISS Search

      │

Relevant Chunks

      │

Gemini
```

---

# End-to-End Request Flow

```text
User Question

        │

Load Conversation Session

        │

Retrieve Recent Messages

        │

Retrieve Relevant Document Chunks

        │

Build Prompt

        │

Gemini API

        │

Assistant Response

        │

Save User Message

        │

Save Assistant Message

        │

Return Response
```

---

# Design Principles

The architecture follows several core principles.

- Modular service-oriented design
- Separation of concerns
- Retrieval-Augmented Generation (RAG)
- Persistent conversation memory
- Explainable AI responses with citations
- Scalable storage architecture
- Extensible AI pipeline

---

# Planned Architecture (Sprint 2)

Sprint 2 extends AlphaLens beyond uploaded documents.

Additional components include:

```text
Company Search

       │

Financial APIs

       │

Market News

       │

Sentiment Analysis

       │

Financial Scoring

       │

Context Builder

       │

Gemini
```

New capabilities:

- Company financial statements
- Financial ratios
- News aggregation
- Sentiment analysis
- Market recommendations
- Company chat

---

# Future Enhancements

The following architectural improvements are planned.

## Advanced Conversation Memory

- Conversation summarization
- Memory embeddings
- Semantic memory retrieval
- Cross-session memory
- Token budget optimization

---

## AI Capabilities

- Multi-agent workflows
- Tool calling
- Function calling
- Streaming responses
- Portfolio analysis
- Watchlists
- Scheduled market monitoring
- Multi-modal document understanding
- MCP (Model Context Protocol) support

---

# Architecture Summary

## Sprint 1 (Implemented)

- Document Processing
- Retrieval-Augmented Generation
- AI Financial Intelligence
- Recommendation Engine
- Multi-document Chat
- Persistent Conversation Memory

## Sprint 2 (Planned)

- Company Intelligence
- News Intelligence
- Sentiment Analysis
- Market Recommendation Engine
- Company Chat

## Sprint 3 (Planned)

- Frontend
- Testing & Evaluation
- Production Deployment