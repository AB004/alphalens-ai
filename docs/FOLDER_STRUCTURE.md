# Folder Structure

```text
alphalens/
│
├── backend/
│   │
│   ├── api/                    # FastAPI route definitions
│   │   ├── auth/
│   │   ├── documents/
│   │   ├── processing/
│   │   ├── rag/
│   │   ├── conversations/
│   │   ├── memory/
│   │   ├── market/
│   │   └── recommendation/
│   │
│   ├── services/               # Business logic
│   │   ├── auth/
│   │   ├── pdf_upload/
│   │   ├── pdf_processing/
│   │   ├── rag/
│   │   ├── conversation/
│   │   ├── memory/
│   │   ├── market/
│   │   ├── sentiment/
│   │   └── recommendation/
│   │
│   ├── repositories/           # Database access layer
│   │
│   ├── models/                 # SQLAlchemy models
│   │
│   ├── schemas/                # Pydantic schemas
│   │
│   ├── middleware/
│   │
│   ├── core/
│   │   ├── config.py
│   │   ├── database.py
│   │   └── security.py
│   │
│   ├── utils/
│   │
│   └── main.py
│
├── ai/
│   │
│   ├── embeddings/
│   │
│   ├── rag/
│   │   ├── chunking/
│   │   ├── indexing/
│   │   ├── retrieval/
│   │   └── citations/
│   │
│   ├── memory/
│   │   ├── conversation_memory.py
│   │   ├── summarizer.py
│   │   ├── memory_embeddings.py
│   │   ├── memory_retriever.py
│   │   └── token_manager.py
│   │
│   ├── context/
│   │   ├── context_builder.py
│   │   ├── prompt_builder.py
│   │   └── prompt_templates.py
│   │
│   ├── financial_analysis/
│   │   ├── summarizer.py
│   │   ├── swot.py
│   │   ├── metric_extractor.py
│   │   ├── risk_analysis.py
│   │   └── opportunity_analysis.py
│   │
│   ├── recommendation/
│   │
│   ├── sentiment/
│   │
│   └── llm/
│       ├── gemini.py
│       └── response_generator.py
│
├── database/
│   ├── migrations/
│   ├── models/
│   └── seed/
│
├── uploads/                    # Uploaded PDFs
│
├── indexes/                    # Persisted FAISS indexes
│
├── memory_store/               # Conversation memory indexes
│
├── frontend/
│   │
│   ├── app/
│   │
│   ├── components/
│   │   ├── chat/
│   │   ├── documents/
│   │   ├── dashboard/
│   │   ├── market/
│   │   └── common/
│   │
│   ├── hooks/
│   │
│   ├── lib/
│   │
│   ├── services/
│   │
│   └── types/
│
├── tests/
│   ├── api/
│   ├── rag/
│   ├── memory/
│   ├── market/
│   └── integration/
│
├── docker/
│
├── configs/
│
├── docs/
│
├── requirements.txt
│
├── .env.example
│
├── README.md
│
└── LICENSE
```

---

# Folder Overview

## backend/

Contains the FastAPI application.

Responsible for:

- API endpoints
- Business logic
- Database interaction
- Authentication
- File management

---

## ai/

Contains all AI-related components.

### embeddings/

Generate embeddings for:

- PDF chunks
- Conversation summaries
- User memories

---

### rag/

Responsible for document retrieval.

Includes:

- Page-aware chunking
- FAISS indexing
- Semantic retrieval
- Citation generation

---

### memory/

Implements ChatGPT-like memory.

Responsible for:

- Conversation history
- Long-term memory
- Conversation summarization
- Semantic memory retrieval
- Token management

---

### context/

Builds the final prompt sent to the LLM.

Combines:

- Recent chat history
- Long-term memory
- Retrieved PDF chunks
- Company financial data
- Market news

---

### financial_analysis/

Performs document intelligence.

Includes:

- Executive summary
- Financial metric extraction
- SWOT generation
- Risk analysis
- Opportunity analysis

---

### sentiment/

Runs FinBERT sentiment analysis on financial news.

---

### recommendation/

Generates explainable Buy / Hold / Sell recommendations.

---

### llm/

Handles interaction with Gemini.

Responsible for:

- Prompt execution
- Response generation
- Output formatting

---

## uploads/

Stores uploaded PDF files.

---

## indexes/

Stores persisted FAISS indexes for document retrieval.

---

## memory_store/

Stores FAISS indexes for long-term conversation memory.

This is separate from document indexes to keep document retrieval and memory retrieval independent.

---

## frontend/

Contains the Next.js application.

Features include:

- Dashboard
- PDF upload
- AI chat
- Market intelligence
- Company comparison
- Conversation history

---

## database/

Contains database-related resources.

- SQLAlchemy models
- Alembic migrations
- Seed scripts

---

## tests/

Contains all automated tests.

- API tests
- Document processing tests
- RAG evaluation
- Memory evaluation
- Market intelligence tests
- Integration tests

---

# Architecture Philosophy

The project is organized around independent modules with clear responsibilities.

```text
Frontend
     │
     ▼

Backend API
     │
     ▼

Business Services
     │
     ▼

AI Layer
     │
     ├───────────────┐
     ▼               ▼

Document RAG    Conversation Memory

     │               │
     └───────┬───────┘
             ▼

      Context Builder

             ▼

         Gemini API

             ▼

      Assistant Response
```

This modular structure makes AlphaLens easy to extend with future capabilities such as multi-agent workflows, tool calling, portfolio analysis, and additional data sources without major architectural changes.