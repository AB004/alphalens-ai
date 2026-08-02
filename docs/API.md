# API Design

## Authentication

POST /auth/register POST /auth/login

## Documents

All routes below are prefixed with `/api`.

| Method | Route | Purpose |
| --- | --- | --- |
| POST | `/documents/upload` | Upload one or more PDFs. Returns persistent document IDs. |
| GET | `/documents` | List uploaded documents and their processing status. |
| DELETE | `/documents/{id}` | Delete document metadata and its stored PDF. |
| POST | `/process` | Extract, clean, and persist PDF text by `document_ids`. |

`POST /upload` remains available as a backwards-compatible upload route.

Example process request:

```json
{"document_ids": [1]}
```

## RAG

POST /chat/document POST /documents/summary

## Market

GET /market/{symbol} GET /market/{symbol}/news GET
/market/{symbol}/sentiment GET /market/{symbol}/recommendation

## Company Chat

POST /chat/company
