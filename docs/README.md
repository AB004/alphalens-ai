# AlphaLens

# AI Financial Research Assistant

AlphaLens is an end-to-end AI Financial Research Assistant built to learn and demonstrate modern AI application development.

Unlike a traditional RAG application, AlphaLens combines document intelligence, long-term conversation memory, market intelligence, and LLM-powered reasoning to provide an interactive financial research experience similar to ChatGPT.

---

# Vision

Build an AI assistant capable of:

- Understanding financial documents
- Remembering previous conversations
- Answering follow-up questions naturally
- Comparing multiple companies
- Combining financial statements, market data, and news
- Providing explainable investment recommendations

---

# Product A — Financial Document Intelligence

Upload one or more financial PDFs and let AlphaLens:

- Upload and manage multiple documents
- Parse and clean PDF text
- Detect text-layout tables
- Create searchable vector indexes
- Chat with one or many PDFs
- Remember previous conversations
- Generate executive summaries
- Extract financial metrics
- Perform SWOT analysis
- Identify risks and opportunities
- Compare multiple annual reports
- Generate explainable Buy / Hold / Sell recommendations

---

## AI Pipeline

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

                     ▲
                     │

          Previous Conversations
                     │
             Conversation Memory
                     │
            Semantic Memory Search

                     ▲
                     │

              Recent Chat History

                     ▼

             Context Builder

                     ▼

                  Gemini

                     ▼

              Assistant Response

                     ▼

       Save Conversation History

                     ▼

      Update Long-Term Memory
```

---

# Product B — Market Intelligence

Search any publicly traded company and let AlphaLens:

- Search companies
- Fetch financial statements
- Calculate financial ratios
- Aggregate market news
- Perform FinBERT sentiment analysis
- Generate financial health scores
- Produce explainable Buy / Hold / Sell recommendations
- Chat using financial data and market news
- Continue conversations across sessions

---

## AI Pipeline

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

## Document Intelligence

- Multiple PDF upload
- Persistent document storage
- PDF parsing and cleaning
- Table detection
- Semantic document search
- Executive summaries
- Financial metric extraction
- SWOT analysis
- Risk identification
- Opportunity detection

---

## Conversation Memory

- Persistent chat sessions
- Multi-turn conversations
- Previous chat retrieval
- Long-term memory
- Conversation summarization
- Cross-session memory
- ChatGPT-like follow-up understanding

---

## Market Intelligence

- Company financials
- Financial ratios
- News aggregation
- Sentiment analysis
- Market recommendation
- Company comparison

---

## AI Recommendations

- Explainable Buy / Hold / Sell
- Confidence score
- Financial reasoning
- Evidence citations
- Educational disclaimer

---

# Technology Stack

## Frontend

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

## AI

- Gemini API
- SentenceTransformers
- FAISS
- FinBERT
- Hybrid Retrieval
- Conversation Memory

---

## Data Sources

- yfinance
- Google News RSS
- Finnhub

---

## Deployment

- Docker

---

# Learning Goals

This project is designed to gain hands-on experience with:

- Retrieval-Augmented Generation (RAG)
- Hybrid Search
- Embeddings
- Vector Databases
- Prompt Engineering
- Context Engineering
- Conversation Memory
- Long-term Memory Systems
- Financial Information Extraction
- Sentiment Analysis
- Recommendation Systems
- AI Application Architecture
- FastAPI
- Next.js
- Full-stack AI Development

---

# Current Progress

## Completed

- PDF Upload & File Management
- PDF Processing
- Page-aware Chunking
- FAISS Vector Indexing
- Semantic Search API

---

## In Progress

- Document Intelligence
- Financial Recommendation Engine
- Multi-document Chat
- Conversation Memory

---

## Planned

- Market Intelligence
- Company Chat
- Frontend Dashboard
- Testing
- Production Deployment

---

# Final Goal

AlphaLens will become a complete AI Financial Research Assistant capable of combining:

- Financial Documents
- Company Financial Data
- Market News
- Sentiment Analysis
- Conversation Memory

into a single conversational AI system that can understand context, remember previous discussions, and provide explainable financial insights.