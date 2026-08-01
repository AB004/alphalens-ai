# Database Design

## Tables

### users

-   id
-   name
-   email
-   password_hash
-   created_at

### documents

-   id
-   user_id
-   file_name
-   company
-   upload_time

### document_chunks

-   id
-   document_id
-   chunk_text
-   embedding_id

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
