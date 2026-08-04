````markdown
# Database Design

## Overview

AlphaLens uses a hybrid storage architecture where different storage systems are responsible for different types of data.

| Storage | Purpose |
|----------|---------|
| SQLite / PostgreSQL | Structured application data |
| File Storage | Uploaded PDF documents |
| FAISS | Document embeddings for semantic retrieval |

SQLite is used during development, while PostgreSQL is recommended for production deployments.

---

# Database Architecture

```text
                        Application

                             │

        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼

 Relational Database     File Storage        Vector Storage
(SQLite/PostgreSQL)         (PDFs)              (FAISS)

        │                    │                    │

 Documents          Uploaded PDF Files    Document Embeddings
 Reports                               Semantic Search Index
 Recommendations
 Conversations
 Chat Messages
```

---

# Current Database Schema (Sprint 1)

The following tables are fully implemented.

---

## documents

Stores uploaded documents together with processed content.

| Column | Description |
|----------|-------------|
| id | Primary key |
| original_filename | Original PDF filename |
| stored_filename | Stored filename |
| storage_path | File location |
| content_type | MIME type |
| size_bytes | File size |
| page_count | Total pages |
| parsed_text | Raw extracted text |
| clean_text | Cleaned document text |
| detected_tables | JSON table information |
| status | uploaded / processed / indexed |
| upload_timestamp | Upload time |
| processed_timestamp | Processing time |

---

## document_chunks

Stores page-aware chunks used during Retrieval-Augmented Generation (RAG).

| Column | Description |
|----------|-------------|
| id | Primary key |
| document_id | Parent document |
| page_number | Source page |
| chunk_index | Chunk order |
| chunk_text | Chunk content |
| token_count | Approximate token count |
| created_at | Timestamp |

---

## document_indexes

Stores metadata about generated FAISS indexes.

| Column | Description |
|----------|-------------|
| id | Primary key |
| document_id | Related document |
| index_path | FAISS index path |
| embedding_model | Embedding model |
| vector_dimension | Embedding dimension |
| chunk_count | Indexed chunks |
| indexed_at | Timestamp |

---

## reports

Stores AI-generated financial analysis.

| Column | Description |
|----------|-------------|
| id | Primary key |
| document_id | Related document |
| executive_summary | AI summary |
| financial_metrics | JSON metrics |
| swot | SWOT analysis |
| risks | Risk analysis |
| opportunities | Opportunity analysis |

---

## recommendations

Stores AI-generated investment recommendations.

| Column | Description |
|----------|-------------|
| id | Primary key |
| document_id | Related document |
| recommendation | Buy / Hold / Sell |
| confidence | Confidence score |
| score | Overall recommendation score |
| reasoning | AI explanation |
| created_at | Timestamp |

---

# Conversation System

---

## conversation_sessions

Represents a persistent chat session.

| Column | Description |
|----------|-------------|
| id | Primary key |
| title | Conversation title |
| document_ids | JSON list of attached documents |
| settings | Chat settings |
| created_at | Created timestamp |
| updated_at | Last activity |

---

## chat_messages

Stores every message exchanged within a conversation.

| Column | Description |
|----------|-------------|
| id | Primary key |
| session_id | Conversation session |
| role | user / assistant |
| message | Message text |
| citations | JSON citations |
| token_count | Optional token count |
| created_at | Timestamp |

---

# Relationships

```text
Document
    │
    ├───────────────┐
    │               │
    ▼               ▼

DocumentChunks    Reports
    │               │
    ▼               ▼

DocumentIndexes  Recommendations


ConversationSession
          │
          ▼

     ChatMessages
```

---

# Storage Responsibilities

## Relational Database

Stores structured application data.

- Documents
- Processed content
- Chunk metadata
- FAISS index metadata
- AI reports
- Recommendations
- Conversation sessions
- Chat messages

---

## File Storage

Stores uploaded PDF files.

---

## FAISS Vector Storage

Stores document embeddings used for semantic retrieval.

### Document Retrieval

```text
Question

        │
        ▼

Question Embedding

        │
        ▼

FAISS Similarity Search

        │
        ▼

Relevant Document Chunks

        │
        ▼

Gemini
```

Document embeddings power AlphaLens' Retrieval-Augmented Generation (RAG) pipeline.

---

# Future Database Schema (Sprint 2+)

The following tables are planned for future releases.

---

## companies

Stores company metadata.

| Column | Description |
|----------|-------------|
| symbol | Stock symbol |
| company_name | Company name |
| sector | Sector |
| industry | Industry |
| exchange | Exchange |

---

## financial_statements

Stores retrieved financial statements.

| Column | Description |
|----------|-------------|
| id | Primary key |
| symbol | Company |
| fiscal_year | Fiscal year |
| statement_type | Balance Sheet / Income Statement / Cash Flow |
| data | JSON financial data |
| updated_at | Timestamp |

---

## news

Stores aggregated financial news.

| Column | Description |
|----------|-------------|
| id | Primary key |
| symbol | Company |
| title | News title |
| summary | Summary |
| source | Publisher |
| url | Article URL |
| published_at | Published timestamp |

---

## sentiment

Stores sentiment analysis results.

| Column | Description |
|----------|-------------|
| id | Primary key |
| news_id | Related article |
| model | FinBERT |
| sentiment | Positive / Neutral / Negative |
| confidence | Confidence score |
| created_at | Timestamp |

---

## market_recommendations

Stores market-wide investment recommendations.

| Column | Description |
|----------|-------------|
| id | Primary key |
| symbol | Company |
| financial_score | Financial score |
| sentiment_score | Sentiment score |
| final_score | Combined score |
| recommendation | Buy / Hold / Sell |
| confidence | Confidence score |
| reasoning | AI explanation |
| generated_at | Timestamp |

---

# Future Conversation Memory

These tables are planned for advanced conversation memory.

---

## conversation_summaries

Stores AI-generated summaries of long conversations.

| Column | Description |
|----------|-------------|
| id | Primary key |
| conversation_id | Conversation |
| summary | AI summary |
| embedding_key | FAISS reference |
| updated_at | Timestamp |

---

## user_memories

Stores persistent user preferences and semantic memories.

Examples:

- Preferred language
- Investment horizon
- Favorite sectors
- Frequently analyzed companies

| Column | Description |
|----------|-------------|
| id | Primary key |
| user_id | Owner |
| memory | Stored memory |
| embedding_key | FAISS reference |
| importance | Priority |
| created_at | Timestamp |

---

# Planned Future Architecture

```text
Question

      │

Conversation Summary
      │

Semantic Memory Search
      │

Recent Chat History
      │

Retrieved Document Chunks
      │

Company Financial Data
      │

Market News
      │

Context Builder
      │

Gemini
```

---

# Why Hybrid Storage?

Different data types require different storage technologies.

### Relational Database

Efficiently stores structured application data and maintains relationships between documents, reports, recommendations, and conversations.

### File Storage

Stores original uploaded PDF files without increasing database size.

### FAISS

Provides fast semantic similarity search over embedded document chunks, enabling efficient Retrieval-Augmented Generation (RAG).

Future versions of AlphaLens will extend FAISS to support semantic conversation memory and long-term user memories.

---

# Summary

## Sprint 1 (Implemented)

- Documents
- Document chunks
- FAISS indexes
- AI reports
- Investment recommendations
- Conversation sessions
- Chat messages

---

## Sprint 2 (Planned)

- Companies
- Financial statements
- News
- Sentiment analysis
- Market recommendations

---

## Future Enhancements

- Conversation summaries
- Semantic memory
- Cross-session memory
- User memory
- Memory embeddings
````
