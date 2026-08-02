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
-   status (`uploaded` or `processed`)
-   parsed_text
-   clean_text
-   tables (JSON)
-   upload_timestamp
-   processed_timestamp

### document_chunks

Planned for Module 3. Chunk metadata must retain the source location required
for citations.

-   id
-   document_id
-   page_number
-   chunk_index
-   chunk_text
-   embedding reference or vector-store key
-   created_at

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
