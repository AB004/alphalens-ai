# AlphaLens AI — API Reference Manual

Base URL: `http://localhost:8000/api`

---

## 1. Document Management & Intelligence (Modules 1 – 6)

### 1.1 Upload Document
- **Endpoint:** `POST /documents/upload`
- **Description:** Upload PDF financial filing, annual report, or prospectus.
- **Request:** `multipart/form-data` with `file: UploadFile`
- **Response:**
```json
{
  "document_id": "doc_12345",
  "filename": "reliance_annual_report_2025.pdf",
  "file_size": 4512030,
  "status": "uploaded",
  "upload_timestamp": "2026-09-27T10:00:00Z"
}
```

### 1.2 Process Document (Text Extraction & Chunking)
- **Endpoint:** `POST /documents/process`
- **Request:**
```json
{ "document_id": "doc_12345", "chunk_size": 500, "chunk_overlap": 50 }
```
- **Response:**
```json
{
  "document_id": "doc_12345",
  "total_pages": 48,
  "total_chunks": 182,
  "status": "processed"
}
```

### 1.3 Index Document (Vector Embedding & FAISS)
- **Endpoint:** `POST /documents/index`
- **Request:**
```json
{ "document_id": "doc_12345" }
```
- **Response:**
```json
{
  "document_id": "doc_12345",
  "indexed_chunks": 182,
  "vector_dimensions": 384,
  "index_status": "ready"
}
```

### 1.4 Semantic Document Search
- **Endpoint:** `GET /documents/search`
- **Query Params:** `query` (str), `top_k` (int, default 5), `document_id` (optional str)
- **Response:**
```json
{
  "query": "EBITDA margin FY25",
  "results": [
    {
      "chunk_id": "chk_01",
      "document_id": "doc_12345",
      "page_number": 12,
      "text": "Consolidated EBITDA for FY25 stood at Rs 1,78,000 Cr...",
      "score": 0.892
    }
  ]
}
```

### 1.5 Document Intelligence (Key Financial Metrics & Summary)
- **Endpoint:** `GET /documents/{document_id}/intelligence`
- **Response:**
```json
{
  "document_id": "doc_12345",
  "executive_summary": "Strong revenue growth led by digital and retail segments...",
  "financial_highlights": { "revenue": 1000000.0, "net_profit": 79000.0, "ebitda_margin": "18.2%" },
  "risk_factors": ["Refining margin volatility", "Foreign exchange fluctuations"]
}
```

### 1.6 Document Recommendations
- **Endpoint:** `GET /documents/{document_id}/recommendations`
- **Response:**
```json
{
  "document_id": "doc_12345",
  "verdict": "Neutral to Bullish",
  "growth_catalysts": ["5G expansion", "Retail footprint expansion"],
  "headwinds": ["High capex intensity"]
}
```

---

## 2. Document & Conversation Chat (Modules 7 – 8)

### 2.1 Create Conversation
- **Endpoint:** `POST /chat/conversations`
- **Request:** `{ "title": "Reliance Q1 Analysis", "document_id": "doc_12345" }`
- **Response:** `{ "conversation_id": "conv_99", "title": "Reliance Q1 Analysis", "created_at": "..." }`

### 2.2 List Conversations
- **Endpoint:** `GET /chat/conversations`
- **Response:** `[ { "conversation_id": "conv_99", "title": "Reliance Q1 Analysis", "message_count": 4 } ]`

### 2.3 Send Message (RAG-Powered Chat)
- **Endpoint:** `POST /chat/messages`
- **Request:**
```json
{
  "conversation_id": "conv_99",
  "message": "What is the management commentary on debt reduction?",
  "document_id": "doc_12345"
}
```
- **Response:**
```json
{
  "message_id": "msg_101",
  "reply": "Management reiterated commitment to maintaining a net debt-zero balance sheet...",
  "cited_sources": [ { "page": 14, "snippet": "Net debt remained negligible..." } ]
}
```

---

## 3. Company & Equity Intelligence (Modules 9 – 10)

### 3.1 Get Company Profile & Financials
- **Endpoint:** `GET /company/{symbol_or_id}`
- **Response:**
```json
{
  "symbol": "TCS",
  "company_name": "Tata Consultancy Services Ltd",
  "sector": "Technology",
  "pe_ratio": 32.1,
  "market_cap": 1560000.0
}
```

### 3.2 Get Company News
- **Endpoint:** `GET /company/{symbol_or_id}/news`
- **Response:**
```json
[
  { "title": "TCS bags $1B mega deal in North America", "source": "Reuters", "published_at": "2026-09-26T08:00:00Z" }
]
```

### 3.3 Financial Sentiment Analysis
- **Endpoint:** `POST /sentiment/analyze`
- **Request:** `{ "text": "Operating profit jumped 24% exceeding street estimates." }`
- **Response:** `{ "sentiment": "Bullish", "score": 0.94, "confidence": 0.98 }`

---

## 4. Home Page & Market Intelligence (Module 11.5)

*Available via both `/home` and `/market` prefixes.*

### 4.1 Consolidated Master Home Dashboard
- **Endpoint:** `GET /home`
- **Description:** Returns the entire Home Page payload in a single roundtrip.
- **Query Params:** `force_refresh` (bool, default `false`)
- **Response:** Single consolidated JSON containing market overview, advance/decline breadth, movers, sectors, earnings, watchlists, 52-week breakouts, volume shockers, and sentiment pulse.

### 4.2 Market Overview & Major Indices
- **Endpoint:** `GET /home/overview`
- **Response:** Indices (Nifty 50, Sensex, Bank Nifty, Nifty IT, S&P 500), trading status (`OPEN`/`CLOSED`/`PRE_MARKET`), and regime (`Bullish`, `Bearish`, `Neutral`).

### 4.3 Advance / Decline Ratio (Market Breadth)
- **Endpoint:** `GET /home/advance-decline`
- **Response:** Total tracked stocks, advances count, declines count, unchanged count, ADR ratio, and breadth sentiment.

### 4.4 Top Gainers, Losers & Most Active
- **Endpoint:** `GET /home/movers`
- **Query Params:** `cap` (`large`, `mid`, `small`, `all`), `limit` (int, default 10)
- **Response:** Partitioned or segmented lists with stock quotes, change %, volume surge ratio.

### 4.5 Sector Performance Heatmap & Movers
- **Endpoint:** `GET /home/sectors` — Sector list with average returns, advances vs declines, top gainer/loser, momentum (`Leading`, `Improving`, `Lagging`, `Weakening`).
- **Endpoint:** `GET /home/sectors/{sector_name}/movers` — Constituents and movers for a given sector.

### 4.6 Quarterly Results (Earnings Announcements)
- **Endpoint:** `GET /home/quarterly-results`
- **Query Params:** `status` (`upcoming`, `recent`, `all`), `limit` (int, default 20)
- **Response:** Revenue, net profit, YoY growth, verdict (`Beat`, `Met`, `Miss`), and stock price impact.

### 4.7 Watchlist
- **Endpoint:** `GET /home/watchlist` — Get user watchlist with live quotes (defaults to bluechip universe).
- **Endpoint:** `POST /home/watchlist` — Add stock: `{ "symbol": "INFY", "category": "tech" }`
- **Endpoint:** `DELETE /home/watchlist/{symbol}` — Remove stock.

### 4.8 52-Week High / Low Breakouts
- **Endpoint:** `GET /home/52-week-high-low`
- **Query Params:** `threshold_percent` (float, default 3.5), `limit` (int, default 10)
- **Response:** Stocks trading within X% of 52-week highs and lows.

### 4.9 Volume Shockers
- **Endpoint:** `GET /home/volume-shockers`
- **Query Params:** `min_ratio` (float, default 1.5), `limit` (int, default 10)
- **Response:** Stocks with current volume significantly exceeding 10-day average.

### 4.10 Market Sentiment Pulse
- **Endpoint:** `GET /home/sentiment`
- **Response:** Market sentiment score (-1.0 to 1.0), bullish/neutral/bearish distribution percentages.

### 4.11 On-Demand Live Market Refresh
- **Endpoint:** `POST /home/refresh`
- **Response:** `{ "status": "success", "indices_updated": 5, "quotes_updated": 32 }`

---

## 5. IPO Intelligence (Official Exchange Data)

*Strictly sourced from NSE / BSE official exchange APIs with resilient fallback.*

### 5.1 Get Upcoming IPOs
- **Endpoint:** `GET /home/ipo/upcoming`
- **Query Params:** `force_refresh` (bool, default `false`)
- **Response:**
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

### 5.2 Get Recent IPOs
- **Endpoint:** `GET /home/ipo/recent`
- **Query Params:** `days` (int, default 30), `force_refresh` (bool, default `false`)
- **Response:** List of IPOs listed within the last `days` period with `listing_price`.

### 5.3 Get IPO Post-Listing Performance
- **Endpoint:** `GET /home/ipo/{symbol}/performance`
- **Query Params:** `limit` (int, default 30), `force_refresh` (bool, default `false`)
- **Response:**
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
