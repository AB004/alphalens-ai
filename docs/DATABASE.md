# Database Design

## Overview

AlphaLens uses a hybrid storage architecture where different storage systems are responsible for different types of data.

| Storage | Purpose |
|---------|---------|
| PostgreSQL / SQLite | Application data |
| File Storage | Uploaded PDF files |
| FAISS | Document and memory embeddings |

During development, SQLite is used as the default database. For production, PostgreSQL is recommended.

---

# Database Architecture

```text
                     Application

                          │

        ┌─────────────────┼──────────────────┐
        ▼                 ▼                  ▼

 Relational DB      File Storage      Vector Storage
(SQLite/PostgreSQL)   (PDFs)             (FAISS)

        │                 │                  │

 Users             Uploaded PDFs      Document Embeddings
 Documents                          Conversation Embeddings
 Conversations                     Memory Embeddings
 Market Data
 Recommendations
```

---

# Tables

## users

Stores registered users.

| Column | Type |
|---------|------|
| id | INTEGER |
| name | TEXT |
| email | TEXT (Unique) |
| password_hash | TEXT |
| created_at | TIMESTAMP |

---

# Financial Document Tables

## documents

Stores uploaded document metadata.

| Column | Description |
|---------|-------------|
| id | Primary key |
| user_id | Owner |
| original_filename | Original PDF name |
| stored_filename | Stored filename |
| storage_path | File path |
| content_type | MIME type |
| size_bytes | File size |
| page_count | Number of pages |
| status | uploaded / processed / indexed |
| upload_timestamp | Upload time |
| processed_timestamp | Processing time |

---

## document_content

Stores processed document content.

| Column | Description |
|---------|-------------|
| id | Primary key |
| document_id | Document |
| parsed_text | Raw extracted text |
| clean_text | Cleaned text |
| detected_tables | JSON table structure |
| processing_status | Processing state |

---

## document_chunks

Stores page-aware chunks used for RAG.

| Column | Description |
|---------|-------------|
| id | Primary key |
| document_id | Parent document |
| page_number | Source page |
| chunk_index | Chunk order |
| chunk_text | Chunk content |
| token_count | Chunk size |
| created_at | Timestamp |

---

## document_indexes

Stores metadata for FAISS indexes.

| Column | Description |
|---------|-------------|
| id | Primary key |
| document_id | Document |
| index_path | Stored FAISS index |
| embedding_model | Embedding model |
| vector_dimension | Embedding dimension |
| chunk_count | Indexed chunks |
| indexed_at | Timestamp |

---

# Conversation System

## conversation_sessions

Each chat is stored as a conversation.

| Column | Description |
|---------|-------------|
| id | Primary key |
| user_id | Owner |
| title | Conversation title |
| type | document / company |
| created_at | Created |
| updated_at | Last activity |

---

## messages

Stores every message exchanged.

| Column | Description |
|---------|-------------|
| id | Primary key |
| conversation_id | Conversation |
| role | user / assistant / system |
| content | Message |
| token_count | Tokens |
| created_at | Timestamp |

---

# Long-Term Memory

Instead of searching every historical message, AlphaLens periodically summarizes conversations.

These summaries become searchable memories.

---

## conversation_summaries

| Column | Description |
|---------|-------------|
| id | Primary key |
| conversation_id | Conversation |
| summary | AI-generated summary |
| embedding_key | FAISS reference |
| updated_at | Last update |

Example

```text
Conversation

Tesla Annual Report

↓

Summary

Revenue growth

Operating Margin

SWOT

Recommendation

↓

Embedding

↓

Memory Retrieval
```

---

## user_memories

Stores persistent user-specific memories.

Examples

- Preferred language
- Investment horizon
- Preferred sectors
- Frequently analyzed companies

| Column | Description |
|---------|-------------|
| id | Primary key |
| user_id | Owner |
| memory | Stored memory |
| embedding_key | FAISS reference |
| importance | Priority |
| created_at | Timestamp |

---

# Market Intelligence

## companies

Stores company information.

| Column | Description |
|---------|-------------|
| symbol | Stock symbol |
| company_name | Company name |
| sector | Sector |
| industry | Industry |
| exchange | Exchange |

---

## financial_statements

Stores retrieved financial data.

| Column | Description |
|---------|-------------|
| id | Primary key |
| symbol | Company |
| fiscal_year | Year |
| statement_type | Balance Sheet / Income Statement / Cash Flow |
| data | JSON |
| updated_at | Timestamp |

---

## news

Stores market news.

| Column | Description |
|---------|-------------|
| id | Primary key |
| symbol | Company |
| title | News title |
| summary | Summary |
| source | Publisher |
| url | Article URL |
| published_at | Publish time |

---

## sentiment

Stores sentiment analysis results.

| Column | Description |
|---------|-------------|
| id | Primary key |
| news_id | Related article |
| model | FinBERT |
| sentiment | Positive / Neutral / Negative |
| confidence | Model confidence |
| created_at | Timestamp |

---

## recommendations

Stores generated investment recommendations.

| Column | Description |
|---------|-------------|
| id | Primary key |
| symbol | Company |
| financial_score | Financial score |
| sentiment_score | Sentiment score |
| final_score | Weighted score |
| recommendation | Buy / Hold / Sell |
| confidence | Confidence |
| reasoning | AI explanation |
| generated_at | Timestamp |

---

# Relationships

```text
User
 │
 ├───────────────┐
 │               │
 ▼               ▼

Documents    Conversations
 │               │
 ▼               ▼

Document      Messages
Content            │
 │                 │
 ▼                 ▼

Chunks     Conversation Summary
 │                 │
 ▼                 ▼

FAISS      Memory Embeddings
```

---

# Storage Responsibilities

## Relational Database

Stores structured application data.

- Users
- Documents
- Parsed content
- Conversations
- Messages
- Financial data
- Recommendations

---

## File Storage

Stores uploaded PDF files.

---

## FAISS Vector Storage

Stores embeddings for semantic retrieval.

### Document Embeddings

Used for document RAG.

```text
Question

↓

Document Search

↓

Relevant Chunks
```

---

### Conversation Embeddings

Used for long-term memory.

```text
Question

↓

Memory Search

↓

Previous Discussion
```

---

# Why Hybrid Storage?

Different data requires different storage mechanisms.

- Relational databases efficiently manage structured data and relationships.
- File storage keeps original PDF files without bloating the database.
- FAISS enables fast semantic search over both document content and conversation memory.

This architecture keeps AlphaLens scalable, modular, and efficient while supporting document intelligence, conversational memory, and market intelligence within a single AI platform.