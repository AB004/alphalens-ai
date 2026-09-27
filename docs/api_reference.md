# AlphaLens AI — Complete API Reference Manual

**Base URL:** `http://localhost:8000/api`  
**Total Endpoints:** 54  
**Authentication:** Optional Session / Bearer Token (where configured)  
**Standard Response:** JSON `application/json` (errors return `{"detail": "..."}`)
**Postman Import:** [`alphalens_ai_postman_collection.json`](file:///h:/Alphalens%20AI/docs/alphalens_ai_postman_collection.json)  

---

## Table of Contents
1. [Document Ingestion & Management](#1-document-ingestion--management) (3 APIs)
2. [Document Processing & Chunking](#2-document-processing--chunking) (1 API)
3. [Document Vector Indexing & Search](#3-document-vector-indexing--search) (2 APIs)
4. [Document Intelligence & Recommendations](#4-document-intelligence--recommendations) (4 APIs)
5. [Document Direct Chat](#5-document-direct-chat) (1 API)
6. [Document Chat Sessions & Messaging](#6-document-chat-sessions--messaging) (6 APIs)
7. [Company Intelligence & Fundamentals](#7-company-intelligence--fundamentals) (7 APIs)
8. [Company News & Counts](#8-company-news--counts) (3 APIs)
9. [Market Recommendations for Equities](#9-market-recommendations-for-equities) (3 APIs)
10. [Company Conversational Chat](#10-company-conversational-chat) (4 APIs)
11. [FinBERT Sentiment Analysis Engine](#11-finbert-sentiment-analysis-engine) (3 APIs)
12. [Home Page & Market Overview](#12-home-page--market-overview) (14 APIs)
13. [IPO Intelligence (Official Exchange)](#13-ipo-intelligence-official-exchange) (3 APIs)

---

## 1. Document Ingestion & Management

### 1.1 Upload PDF Documents
- **`POST /documents/upload`**
- **Description:** Upload one or more PDF financial documents (annual reports, earnings transcripts, DRHP).
- **Request:** `multipart/form-data` with `files: List[UploadFile]`
- **Response:** `UploadResponse`
```json
{
  "message": "Files uploaded successfully",
  "documents": [
    {
      "id": 1,
      "filename": "reliance_q1_fy25.pdf",
      "file_path": "uploads/reliance_q1_fy25.pdf",
      "file_size": 2450890,
      "uploaded_at": "2026-09-27T10:00:00Z"
    }
  ]
}
```

### 1.2 List Uploaded Documents
- **`GET /documents`**
- **Description:** Retrieve list of all uploaded financial documents stored in the system.
- **Request:** None
- **Response:** `DocumentListResponse`
```json
{
  "documents": [
    {
      "id": 1,
      "filename": "reliance_q1_fy25.pdf",
      "file_size": 2450890,
      "uploaded_at": "2026-09-27T10:00:00Z"
    }
  ]
}
```

### 1.3 Delete Document
- **`DELETE /documents/{document_id}`**
- **Description:** Remove a document record, chunk index, and stored file from disk.
- **Path Params:** `document_id: int`
- **Response:** `204 No Content`

---

## 2. Document Processing & Chunking

### 2.1 Process Document Chunks
- **`POST /documents/process`**
- **Description:** Extracts raw text from uploaded PDF, generates semantic chunks with metadata (page numbers, section headers).
- **Request Body:**
```json
{
  "document_id": 1,
  "chunk_size": 500,
  "chunk_overlap": 50
}
```
- **Response:** `ProcessResponse`
```json
{
  "document_id": 1,
  "total_pages": 32,
  "chunks_created": 128,
  "status": "completed"
}
```

---

## 3. Document Vector Indexing & Search

### 3.1 Build Document FAISS Vector Index
- **`POST /documents/{document_id}/index`**
- **Description:** Embeds processed chunks using SentenceTransformers and builds FAISS vector index.
- **Path Params:** `document_id: int`
- **Request Body:** `{ "force_reindex": false }`
- **Response:** `IndexResponse`
```json
{
  "document_id": 1,
  "total_indexed": 128,
  "vector_dimensions": 384,
  "status": "indexed"
}
```

### 3.2 Semantic Similarity Search
- **`POST /documents/{document_id}/search`**
- **Description:** Perform semantic vector retrieval against indexed document chunks.
- **Path Params:** `document_id: int`
- **Request Body:**
```json
{
  "query": "What is the net profit and EBITDA margin for Q1?",
  "top_k": 5
}
```
- **Response:** `SearchResponse`
```json
{
  "query": "What is the net profit and EBITDA margin for Q1?",
  "results": [
    {
      "chunk_id": 14,
      "page_number": 6,
      "score": 0.884,
      "text": "EBITDA margin stood at 18.2% with net profit of Rs 15,138 Cr..."
    }
  ]
}
```

---

## 4. Document Intelligence & Recommendations

### 4.1 Generate Document Intelligence Analysis
- **`POST /documents/{document_id}/analysis`**
- **Description:** Uses LLM (Gemini / Claude) to synthesize an executive summary, financial ratios, growth drivers, and risk factors from document chunks.
- **Path Params:** `document_id: int`
- **Response:** `ReportResponse`
```json
{
  "document_id": 1,
  "executive_summary": "Strong revenue acceleration in retail and telecom offsets O2C margin pressure...",
  "financial_highlights": { "revenue": 236217.0, "net_profit": 15138.0 },
  "risks": ["Crude oil refining volatility", "High 5G capex"],
  "created_at": "2026-09-27T10:15:00Z"
}
```

### 4.2 Retrieve Saved Document Intelligence Analysis
- **`GET /documents/{document_id}/analysis`**
- **Description:** Fetches previously generated document intelligence report from database.
- **Path Params:** `document_id: int`
- **Response:** `ReportResponse`

### 4.3 Generate Investment Recommendation
- **`POST /documents/{document_id}/recommendation`**
- **Description:** Generates structured investment verdict (Bullish / Neutral / Bearish) with risk-reward rationale.
- **Path Params:** `document_id: int`
- **Response:** `RecommendationResponse`
```json
{
  "document_id": 1,
  "verdict": "Bullish",
  "target_horizon": "12-18 months",
  "rationale": "High operating leverage, strong retail margins, subscriber monetization.",
  "confidence_score": 0.85
}
```

### 4.4 Retrieve Saved Recommendation
- **`GET /documents/{document_id}/recommendation`**
- **Description:** Fetches stored investment recommendation for a document.
- **Path Params:** `document_id: int`
- **Response:** `RecommendationResponse`

---

## 5. Document Direct Chat

### 5.1 One-Shot Document Q&A
- **`POST /documents/chat`**
- **Description:** Stateless RAG question-answering over an indexed document.
- **Request Body:**
```json
{
  "document_id": 1,
  "question": "What deal wins were announced in North America?"
}
```
- **Response:** `ChatResponse`
```json
{
  "answer": "Management highlighted $8.3B TCV deal wins with large financial institutions...",
  "citations": [ { "page": 12, "chunk_id": 45 } ]
}
```

---

## 6. Document Chat Sessions & Messaging

### 6.1 Create Chat Session
- **`POST /chat/sessions`**
- **Description:** Create a persistent conversation session tied to a document.
- **Request Body:** `{ "title": "Reliance Q1 Review", "document_id": 1 }`
- **Response:** `ConversationResponse` (`id`, `title`, `document_id`, `created_at`)

### 6.2 List All Chat Sessions
- **`GET /chat/sessions`**
- **Description:** Returns all conversation sessions.
- **Response:** `list[ConversationResponse]`

### 6.3 Get Specific Chat Session
- **`GET /chat/sessions/{session_id}`**
- **Path Params:** `session_id: int`
- **Response:** `ConversationResponse`

### 6.4 Delete Chat Session
- **`DELETE /chat/sessions/{session_id}`**
- **Description:** Delete session and all associated messages.
- **Path Params:** `session_id: int`
- **Response:** `{"message": "Session deleted"}`

### 6.5 Send Message in Session (Multi-Turn RAG)
- **`POST /chat/sessions/{session_id}/messages`**
- **Description:** Sends user message, retrieves context, queries LLM, records turn in history.
- **Path Params:** `session_id: int`
- **Request Body:** `{ "content": "How does this compare to Q4?" }`
- **Response:** `ConversationMessageResponse`
```json
{
  "message_id": 42,
  "session_id": 3,
  "role": "assistant",
  "content": "Sequentially, revenue increased by 3.2% compared to Q4 FY24...",
  "sources": [ { "page": 8, "text": "QoQ growth stood at 3.2%..." } ],
  "timestamp": "2026-09-27T10:20:00Z"
}
```

### 6.6 Get Message History of Session
- **`GET /chat/sessions/{session_id}/messages`**
- **Description:** Get all past messages in chronological order.
- **Path Params:** `session_id: int`
- **Response:** `list[MessageResponse]`

---

## 7. Company Intelligence & Fundamentals

### 7.1 Search Companies
- **`GET /company/search`**
- **Query Params:** `q: str`, `limit: int = 10`
- **Response:** List of matching company profiles (`symbol`, `company_name`, `sector`).

### 7.2 Get Company Fundamental Profile
- **`GET /company/{symbol}`**
- **Path Params:** `symbol: str` (e.g., `TCS`, `RELIANCE`)
- **Response:**
```json
{
  "symbol": "TCS",
  "company_name": "Tata Consultancy Services Ltd",
  "sector": "Technology",
  "market_cap": 1560000.0,
  "pe_ratio": 32.1,
  "high_52w": 4592.25,
  "low_52w": 3313.00
}
```

### 7.3 Get Detailed Financials
- **`GET /company/{symbol}/financials`**
- **Description:** Returns annual/quarterly financial statements, margins, and ratios.
- **Path Params:** `symbol: str`
- **Response:** Detailed financial dictionary (Revenue, EBITDA, Net Margin, EPS, ROE).

### 7.4 On-Demand Refresh Company Data
- **`POST /company/{symbol}/refresh`**
- **Description:** Triggers live re-fetch from market provider for company metadata.
- **Path Params:** `symbol: str`
- **Response:** `{"message": "Company data refreshed", "symbol": "TCS"}`

### 7.5 List Tracked Companies
- **`GET /company`**
- **Query Params:** `skip: int = 0`, `limit: int = 50`
- **Response:** Paginated list of tracked company records.

### 7.6 Get Aggregated Company Sentiment
- **`GET /company/{symbol}/sentiment`**
- **Path Params:** `symbol: str`
- **Response:** `{ "symbol": "TCS", "sentiment_score": 0.65, "label": "Bullish", "articles_analyzed": 48 }`

### 7.7 Trigger Company Sentiment Analysis
- **`POST /company/{symbol}/sentiment/analyze`**
- **Path Params:** `symbol: str`, `limit: int = 100`
- **Response:** Freshly calculated sentiment breakdown across news items.

---

## 8. Company News & Counts

### 8.1 Get Company News Articles
- **`GET /company/{symbol}/news`**
- **Path Params:** `symbol: str`
- **Query Params:** `limit: int = 20`
- **Response:** List of news items (`id`, `title`, `url`, `source`, `published_at`, `sentiment_label`).

### 8.2 Get Company News Count
- **`GET /company/{symbol}/news/count`**
- **Path Params:** `symbol: str`
- **Response:** `{ "symbol": "TCS", "total_news_articles": 134 }`

### 8.3 Refresh Company News
- **`POST /company/{symbol}/news/refresh`**
- **Path Params:** `symbol: str`
- **Response:** `NewsRefreshResponse` (`new_articles_count`, `symbol`)

---

## 9. Market Recommendations for Equities

### 9.1 Get Current Market Recommendation
- **`GET /company/{symbol}/recommendation`**
- **Path Params:** `symbol: str`
- **Response:** Current recommendation, confidence level, and key catalyst factors.

### 9.2 Analyze and Generate New Recommendation
- **`POST /company/{symbol}/recommendation/analyze`**
- **Path Params:** `symbol: str`
- **Query Params:** `sentiment_limit: int = 100`
- **Response:** Newly evaluated recommendation combining technicals, sentiment, and earnings.

### 9.3 Get Recommendation History
- **`GET /company/{symbol}/recommendations`**
- **Path Params:** `symbol: str`
- **Query Params:** `skip: int = 0`, `limit: int = 20`
- **Response:** Historical audit log of recommendation changes over time.

---

## 10. Company Conversational Chat

### 10.1 Ask Question About Company
- **`POST /company/{symbol}/chat`**
- **Path Params:** `symbol: str`
- **Request Body:**
```json
{
  "message": "What is the valuation view on TCS given the recent deal wins?",
  "conversation_id": null
}
```
- **Response:** `CompanyChatResponse`
```json
{
  "conversation_id": 5,
  "reply": "TCS is currently trading at a P/E of 32.1x, in line with its 5-year average...",
  "symbol": "TCS"
}
```

### 10.2 Get Company Conversation Details
- **`GET /company/{symbol}/chat/{conversation_id}`**
- **Path Params:** `symbol: str`, `conversation_id: int`
- **Response:** `CompanyConversationResponse`

### 10.3 List All Chats for a Company
- **`GET /company/{symbol}/chats`**
- **Path Params:** `symbol: str`
- **Response:** List of company conversation summaries.

### 10.4 Get Messages in Company Chat
- **`GET /company/{symbol}/chat/{conversation_id}/messages`**
- **Path Params:** `symbol: str`, `conversation_id: int`
- **Response:** List of user and assistant messages for this company conversation.

---

## 11. FinBERT Sentiment Analysis Engine

### 11.1 Get Sentiment for a News Article
- **`GET /sentiment/news/{news_id}`**
- **Path Params:** `news_id: int`
- **Response:** `{ "news_id": 12, "sentiment": "positive", "score": 0.94 }`

### 11.2 Trigger Sentiment Scoring on News Article
- **`POST /sentiment/news/{news_id}`**
- **Path Params:** `news_id: int`
- **Query Params:** `force: bool = false`
- **Response:** FinBERT evaluated sentiment classification (`positive`, `neutral`, `negative`).

### 11.3 Get Comprehensive Company Sentiment Pulse
- **`GET /sentiment/company/{symbol}`**
- **Path Params:** `symbol: str`
- **Query Params:** `limit: int = 100`
- **Response:**
```json
{
  "symbol": "RELIANCE",
  "overall_sentiment": "Bullish",
  "sentiment_score": 0.42,
  "positive_pct": 62.0,
  "neutral_pct": 24.0,
  "negative_pct": 14.0,
  "sample_size": 85
}
```

---

## 12. Home Page & Market Overview

*(Also available under prefix `/api/market`)*

### 12.1 Consolidated Master Home Page Dashboard
- **`GET /home`**
- **Description:** Complete master dashboard payload in 1 roundtrip (overview, breadth, movers, sectors, earnings, watchlists, 52w extremes, volume shockers, sentiment).
- **Query Params:** `force_refresh: bool = false`
- **Response:** `HomeDashboardResponse`

### 12.2 Market Overview & Major Indices
- **`GET /home/overview`**
- **Description:** Live values for Nifty 50, Sensex, Bank Nifty, Nifty IT, S&P 500, exchange hours status, and market regime.
- **Query Params:** `force_refresh: bool = false`
- **Response:** `MarketOverviewResponse`

### 12.3 Advance / Decline Ratio (Market Breadth)
- **`GET /home/advance-decline`**
- **Description:** Advances, declines, unchanged counts, Advance/Decline Ratio (ADR), and breadth sentiment.
- **Query Params:** `force_refresh: bool = false`
- **Response:** `AdvanceDeclineResponse`

### 12.4 Top Gainers, Losers & Most Active
- **`GET /home/movers`**
- **Query Params:**
  - `cap: str = "all"` (`large`, `mid`, `small`, `all`)
  - `limit: int = 10`
  - `force_refresh: bool = false`
- **Response:** `MarketMoversResponse`

### 12.5 Sector Performance Heatmap
- **`GET /home/sectors`**
- **Description:** Sector returns, advances vs declines, top gainer/loser, and momentum (`Leading`, `Improving`, `Lagging`, `Weakening`).
- **Query Params:** `force_refresh: bool = false`
- **Response:** `List[SectorPerformanceItem]`

### 12.6 Specific Sector Movers
- **`GET /home/sectors/{sector_name}/movers`**
- **Path Params:** `sector_name: str` (e.g., `Technology`, `Automobile`)
- **Query Params:** `force_refresh: bool = false`
- **Response:** `SectorMoversResponse`

### 12.7 Quarterly Results & Earnings Announcements
- **`GET /home/quarterly-results`**
- **Query Params:**
  - `status: str = "all"` (`upcoming`, `recent`, `all`)
  - `limit: int = 20`
  - `force_refresh: bool = false`
- **Response:** `QuarterlyResultsListResponse`

### 12.8 Get Watchlist with Live Quotes
- **`GET /home/watchlist`**
- **Query Params:** `user_id: str = "default"`, `force_refresh: bool = false`
- **Response:** `WatchlistResponse`

### 12.9 Add Stock to Watchlist
- **`POST /home/watchlist`**
- **Request Body:**
```json
{
  "symbol": "INFY",
  "user_id": "default",
  "category": "bluechip",
  "notes": "Top Indian IT leader"
}
```
- **Response:** `201 Created` with added item details.

### 12.10 Remove Stock from Watchlist
- **`DELETE /home/watchlist/{symbol}`**
- **Path Params:** `symbol: str`
- **Query Params:** `user_id: str = "default"`
- **Response:** `{"symbol": "INFY", "removed": true}`

### 12.11 52-Week High & Low Breakouts
- **`GET /home/52-week-high-low`**
- **Query Params:** `threshold_percent: float = 3.5`, `limit: int = 10`
- **Response:** `HighLow52WeekResponse`

### 12.12 Volume Shockers
- **`GET /home/volume-shockers`**
- **Description:** Stocks trading with volume surging >= `min_ratio` compared to 10-day average.
- **Query Params:** `min_ratio: float = 1.5`, `limit: int = 10`
- **Response:** `List[StockQuoteResponse]`

### 12.13 Market Sentiment Pulse
- **`GET /home/sentiment`**
- **Description:** Market-wide aggregated sentiment breakdown (Bullish/Neutral/Bearish) and composite score.
- **Response:** `MarketSentimentPulseResponse`

### 12.14 Trigger On-Demand Market Refresh
- **`POST /home/refresh`**
- **Description:** Forces live external market provider re-fetch for all tracked indices and equities.
- **Response:** `RefreshStatusResponse` (`indices_updated`, `quotes_updated`, `status`)

---

## 13. IPO Intelligence (Official Exchange)

*Strictly sourced from NSE / BSE official exchange APIs with zero third-party scrapers.*

### 13.1 Get Upcoming IPOs
- **`GET /home/ipo/upcoming`**
- **Description:** Live active and forthcoming IPO issues sourced from NSE official API.
- **Query Params:** `force_refresh: bool = false`
- **Response:** `List[dict]`
```json
[
  {
    "id": 1,
    "company_name": "Runwal Enterprises Limited",
    "symbol": "RUNWALENTR",
    "exchange": "mainboard",
    "issue_date": "2026-09-25",
    "price_range_low": 290.0,
    "price_range_high": 302.0,
    "total_shares": 12111294,
    "listing_price": null,
    "underwriters": "NSE Registered Book Running Lead Managers",
    "status": "upcoming"
  }
]
```

### 13.2 Get Recent IPOs
- **`GET /home/ipo/recent`**
- **Description:** IPOs listed within the last `days` period.
- **Query Params:** `days: int = 30`, `force_refresh: bool = false`
- **Response:** `List[dict]`

### 13.3 Get IPO Post-Listing Performance
- **`GET /home/ipo/{symbol}/performance`**
- **Description:** Daily OHLCV trading records and returns for a listed IPO.
- **Path Params:** `symbol: str` (e.g., `BAJAJHFL`)
- **Query Params:** `limit: int = 30`, `force_refresh: bool = false`
- **Response:** `List[dict]`
```json
[
  {
    "id": 1,
    "ipo_id": 4,
    "trade_date": "2026-09-26",
    "open_price": 145.0,
    "close_price": 152.4,
    "high_price": 155.0,
    "low_price": 142.5,
    "volume": 4200000,
    "pct_change": 5.1
  }
]
```
