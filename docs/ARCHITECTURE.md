# AlphaLens Architecture

## Overview

AlphaLens is an AI Financial Research Assistant designed to analyze financial documents, understand market data, and maintain conversational memory across multiple sessions.

The system combines Retrieval-Augmented Generation (RAG), conversation memory, financial analysis, and market intelligence into a single AI-powered platform.

The architecture is divided into four major layers:

1. Financial Document Intelligence
2. Conversation & Memory System
3. Market Intelligence
4. AI Reasoning Layer

---

# High-Level Architecture

```text
                           User
                             │
                             ▼
                     FastAPI Backend
                             │
         ┌───────────────────┼───────────────────┐
         ▼                   ▼                   ▼

 Financial Documents   Conversation Memory   Market Intelligence

         │                   │                   │

         ▼                   ▼                   ▼

   PDF Processing      Recent Chat        Financial APIs
         │             Memory Search          News APIs
         │                   │                   │
         ▼                   ▼                   ▼

   Vector Database      Memory Store      Sentiment Analysis

         └───────────────────┼───────────────────┘
                             ▼

                     Context Builder

                             ▼

                     Prompt Engineering

                             ▼

                         Gemini API

                             ▼

                     Assistant Response

                             ▼

              Conversation Persistence

                             ▼

             Long-Term Memory Update
```

---

# System Components

## 1. Financial Document Intelligence

Responsible for understanding uploaded financial reports.

### Workflow

```text
PDF Upload
      │
      ▼
Validation
      │
      ▼
Text Extraction
      │
      ▼
Cleaning
      │
      ▼
Table Detection
      │
      ▼
Database Storage
      │
      ▼
Page-aware Chunking
      │
      ▼
SentenceTransformer Embeddings
      │
      ▼
FAISS Index
```

### Responsibilities

- Upload multiple PDFs
- Validate files
- Extract text
- Detect text-layout tables
- Clean extracted content
- Generate page-aware chunks
- Create embeddings
- Persist FAISS indexes
- Support semantic search

---

# 2. Conversation & Memory System

Unlike a traditional RAG application, AlphaLens remembers previous conversations.

The memory system is divided into two layers.

## Short-Term Memory

Maintains recent conversation history.

Used for:

- Follow-up questions
- Pronoun resolution
- Multi-turn conversations

Example

```text
User:
Summarize Tesla's report.

↓

Assistant:
...

↓

User:
Explain the second risk.

↓

The assistant understands
"second risk"
using recent chat history.
```

---

## Long-Term Memory

Stores summarized conversations for future sessions.

Instead of storing every message forever, AlphaLens periodically generates conversation summaries.

These summaries are converted into embeddings and indexed for semantic retrieval.

Example

```text
Conversation Summary

Company:
Tesla

Topics:
Revenue
Margins
SWOT
Recommendation

Final Recommendation:
Hold
```

When the user later asks:

> Compare it with Nvidia.

The memory retrieval system finds the previous Tesla discussion and includes it in the prompt automatically.

---

# Memory Architecture

```text
Conversation

        │

Recent Messages
(SQL Database)

        │

Conversation Summary

        │

Embedding

        │

FAISS Memory Index

        │

Semantic Retrieval
```

---

# 3. Market Intelligence

Provides real-time company information.

### Workflow

```text
Company Symbol

       │

       ▼

Financial APIs

       │

       ▼

News Collection

       │

       ▼

Deduplication

       │

       ▼

FinBERT Sentiment

       │

       ▼

Financial Analysis
```

Responsibilities

- Company search
- Financial statements
- Financial ratios
- News aggregation
- Sentiment analysis
- Market recommendations

---

# 4. AI Reasoning Layer

This is the core intelligence layer.

Every user request is processed through a context-building pipeline.

```text
User Question

        │

        ▼

Recent Chat Retrieval

        │

Memory Retrieval

        │

Document Retrieval

        │

Market Retrieval

        │

Merge Context

        │

Prompt Builder

        │

Gemini API

        │

Assistant Response
```

---

# Context Builder

The Context Builder is responsible for combining information from multiple sources into a single prompt.

Sources include:

- Recent conversation history
- Long-term conversation memory
- Financial document retrieval
- Company financial data
- Market news
- Sentiment analysis

This hybrid context enables natural conversations while grounding responses in factual evidence.

---

# Data Storage

AlphaLens uses multiple storage systems optimized for different workloads.

## Relational Database

Stores structured application data.

Examples:

- Users
- Documents
- Messages
- Conversation sessions
- Financial metrics
- Recommendations

---

## File Storage

Stores uploaded PDF files.

---

## Vector Database (FAISS)

Stores embeddings for:

- Document chunks
- Conversation summaries
- Long-term memory

---

# End-to-End Request Flow

```text
User Question
        │
        ▼

Load Conversation

        │
        ▼

Retrieve Recent Messages

        │
        ▼

Retrieve Long-Term Memories

        │
        ▼

Retrieve Relevant PDF Chunks

        │
        ▼

Retrieve Market Information
(if required)

        │
        ▼

Context Builder

        │
        ▼

Prompt Engineering

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

Update Memory
```

---

# Design Principles

The architecture follows these principles:

- Modular services
- Separation of concerns
- Stateless APIs with persistent memory
- Hybrid Retrieval (Memory + RAG + Market Data)
- Explainable AI responses with citations
- Scalable storage architecture
- Production-ready deployment
- Extensible AI pipeline for future agents and tools

---

# Future Enhancements

Planned architectural improvements include:

- Multi-agent orchestration
- Tool calling
- Function calling
- Portfolio analysis
- Watchlists
- Scheduled market monitoring
- Streaming LLM responses
- Multi-modal document understanding
- Knowledge graph integration
- MCP (Model Context Protocol) support