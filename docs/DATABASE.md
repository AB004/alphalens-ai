# Database Design

## Tables

### users

-   id
-   name
-   email
-   password_hash
-   created_at

### documents

Implemented in Modules 1 and 2. The development default is SQLite at
`alphalens.db`; set `DATABASE_URL` for another SQLAlchemy-supported database.

-   id
-   original_filename
-   stored_filename
-   storage_path
-   content_type
-   size_bytes
-   page_count
-   status (`uploaded`, `processed`, or `indexed`)
-   parsed_text
-   clean_text
-   tables (JSON)
-   upload_timestamp
-   processed_timestamp

### document_chunks

Implemented in Module 3. Chunk metadata retains the source location required
for citations.

-   id
-   document_id
-   page_number
-   chunk_index
-   chunk_text
-   embedding reference or vector-store key
-   created_at

### document_indexes

Implemented in Module 3. Each document has one persisted FAISS index.

-   id
-   document_id
-   index_path
-   embedding_model
-   vector_dimension
-   chunk_count
-   indexed_at

### chat_sessions

-   id
-   user_id
-   type (document/company)

### chat_messages

-   id
-   session_id
-   role
-   message

### stock_cache

-   symbol
-   company_name
-   financial_data
-   updated_at

### news

-   id
-   symbol
-   title
-   summary
-   sentiment
-   source
-   published_at

### recommendations

-   id
-   symbol
-   score
-   recommendation
-   confidence
-   reasons
