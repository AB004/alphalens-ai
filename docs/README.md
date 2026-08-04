# AlphaLens

# AI Financial Research Assistant

AlphaLens is an end-to-end AI Financial Research Assistant built to learn and demonstrate modern AI application development.

It combines document intelligence, retrieval-augmented generation (RAG), persistent conversation memory, and explainable AI to create an interactive financial research assistant capable of understanding financial reports and answering complex financial questions.

---

# Vision

Build an AI assistant capable of:

- Understanding financial documents
- Remembering conversation history
- Answering follow-up questions naturally
- Comparing multiple financial reports
- Combining financial statements, market data, and news
- Providing explainable investment recommendations

---

# Product A — Financial Document Intelligence

Upload one or more financial PDFs and let AlphaLens:

- Upload and manage multiple documents
- Parse and clean PDF text
- Detect text-layout tables
- Create searchable vector indexes
- Chat with one or multiple PDFs
- Maintain persistent conversation history
- Generate executive summaries
- Extract financial metrics
- Perform SWOT analysis
- Identify risks and opportunities
- Compare multiple annual reports
- Generate explainable Buy / Hold / Sell recommendations

---

# AI Pipeline

```text
                PDF Upload
                     │
                     ▼
            PDF Processing
                     │
                     ▼
          Page-aware Chunking
                     │
                     ▼
      SentenceTransformer Embeddings
                     │
                     ▼
                 FAISS Index
                     │
                     ▼
            Semantic Retrieval
                     │
                     ▼
        Previous Conversation History
                     │
                     ▼
             Context Builder
                     │
                     ▼
                  Gemini
                     │
                     ▼
             Assistant Response
                     │
                     ▼
       Store Conversation History
```

---

# Product B — Market Intelligence *(Sprint 2)*

Search any publicly traded company and let AlphaLens:

- Search companies
- Fetch financial statements
- Calculate financial ratios
- Aggregate market news
- Perform FinBERT sentiment analysis
- Generate financial health scores
- Produce explainable Buy / Hold / Sell recommendations
- Chat using financial data and market news
- Continue conversations naturally

---

# Planned AI Pipeline

```text
Company Symbol
       │
       ▼
 Financial APIs
       │
 News APIs
       │
 Sentiment Analysis
       │
 Financial Analysis
       │
 Conversation Memory
       │
 Context Builder
       │
 Gemini
       │
 AI Response
```

---

# Core Features

## Financial Document Intelligence

- Multiple PDF upload
- Persistent document storage
- PDF parsing and cleaning
- Table detection
- Semantic document retrieval
- Executive summaries
- Financial metric extraction
- SWOT analysis
- Risk identification
- Opportunity detection
- Multi-document comparison

---

## AI Chat & Conversation Memory

- Persistent chat sessions
- Multi-turn conversations
- Conversation history
- Follow-up question understanding
- Citation-aware responses
- Context-aware prompting

> **Planned Enhancements**
>
> - Conversation summarization
> - Long-term semantic memory
> - Cross-session memory
> - Token tracking
> - Token budget optimization

---

## Financial Recommendation Engine

- Explainable Buy / Hold / Sell recommendations
- Confidence score
- Financial reasoning
- Supporting evidence
- Educational disclaimer

---

## Market Intelligence *(Planned)*

- Company financials
- Financial ratios
- News aggregation
- Sentiment analysis
- Company comparison
- AI-powered company chat

---

# Technology Stack

## Frontend *(Planned)*

- Next.js
- TypeScript
- Tailwind CSS

---

## Backend

- FastAPI
- SQLAlchemy
- SQLite (Development)
- PostgreSQL (Production)

---

## AI & Machine Learning

- Gemini API
- SentenceTransformers
- FAISS
- FinBERT *(Planned)*
- Retrieval-Augmented Generation (RAG)

---

## Data Sources *(Sprint 2)*

- yfinance
- Google News RSS
- Finnhub

---

## Deployment *(Sprint 3)*

- Docker

---

# Learning Goals

This project is designed to gain hands-on experience with:

- Retrieval-Augmented Generation (RAG)
- Vector Search
- Embeddings
- FAISS
- Prompt Engineering
- Context Engineering
- Conversation Memory
- Financial Information Extraction
- Explainable AI
- Recommendation Systems
- FastAPI
- Next.js
- Full-stack AI Development

---

# Current Progress

## ✅ Sprint 1 Complete

### Completed

- ✅ PDF Upload & File Management
- ✅ PDF Processing
- ✅ Page-aware Chunking
- ✅ FAISS Vector Indexing
- ✅ Semantic Search
- ✅ Document Intelligence
- ✅ Financial Recommendation Engine
- ✅ Multi-document Chat
- ✅ Persistent Conversation Memory

---

## 🚧 Sprint 2

- Company Intelligence
- News Engine
- Sentiment Analysis
- Market Recommendation Engine
- Company Chat

---

## 🚀 Sprint 3

- Frontend Dashboard
- Testing & Evaluation
- Production Deployment

---

# Project Status

| Sprint | Status |
|---------|--------|
| Sprint 1 – Financial Document Intelligence | ✅ Complete |
| Sprint 2 – Market Intelligence | 🚧 Planned |
| Sprint 3 – Production | 🚧 Planned |

---

# Final Goal

AlphaLens aims to become a complete AI Financial Research Assistant capable of combining:

- Financial Documents
- Company Financial Data
- Market News
- Sentiment Analysis
- Retrieval-Augmented Generation (RAG)
- Persistent Conversation Memory
- Explainable AI

into a unified conversational platform that understands financial information, maintains conversation context, and delivers trustworthy, citation-aware financial insights.