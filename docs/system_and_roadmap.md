# AlphaLens AI — System Overview & Future Roadmap

---

## 1. System Architecture Summary

AlphaLens AI is an institutional-grade financial intelligence platform uniting **RAG-powered document intelligence** (filings, transcripts, annual reports) with **real-time market overview analytics** (indices, market breadth, sector heatmaps, earnings, and IPOs).

```
[ Frontend: Next.js / Tailwind / Shadcn UI ]
                    │
                    ▼  (REST / WebSocket)
[ FastAPI Gateway  /api ]
   ├── /documents  ─── PDF Pipeline ──> PyPDF Chunking ──> FAISS Vector Store
   ├── /chat       ─── Financial RAG ──> Gemini / Claude / DeepSeek LLM
   ├── /company    ─── Equity Intelligence & News Sentiment (FinBERT)
   └── /home       ─── Market Engine ──> Multi-Tier Resilient Cache (Postgres / NSE-BSE)
```

### Core Design Principles:
1. **Multi-Tier Resilient Caching:** Database Cache ➔ Live Exchange Provider ➔ Curated Fallback Seed. Guarantees zero empty API responses.
2. **Strict Official Exchange Sourcing:** IPO and market breadth data connect strictly to official NSE/BSE endpoints or fall back cleanly.
3. **High Cohesion & Low Coupling:** Clean separation between Controllers (`api/`), Services (`services/`), Models (`models/`), and Data Access (`repositories/`).

---

## 2. Directory Layout

```
Alphalens AI/
├── backend/
│   ├── api/                  # FastAPI routers
│   │   ├── documents/        # Upload, parsing, indexing, search
│   │   ├── document_chat/    # Conversation history & messaging
│   │   ├── company/          # Profile, news, recommendations
│   │   ├── sentiment/        # FinBERT financial sentiment
│   │   ├── home/             # Home page & IPO endpoints
│   │   └── router.py         # Root API router mounting
│   ├── models/               # SQLAlchemy ORM models (Quotes, IPOs, Chunks, etc.)
│   ├── repositories/         # Database persistence queries
│   ├── schemas/              # Pydantic v2 schemas (validation & serialization)
│   ├── services/             # Core business logic & market providers
│   │   ├── market/           # HomeService, NSE Provider, Yahoo Provider
│   │   ├── pdf_processing/   # PDF chunking and parsing
│   │   ├── rag/              # FAISS embedding and retriever
│   │   └── sentiment/        # Financial sentiment scoring
│   ├── database/             # PostgreSQL engine & session factory
│   └── main.py               # Application entrypoint
├── docs/
│   ├── api_reference.md      # Consolidated API documentation
│   └── system_and_roadmap.md # Architecture & future roadmap
└── requirements.txt          # Python dependencies
```

---

## 3. Future Roadmap: Frontend Implementation

### 3.1 Tech Stack
- **Framework:** Next.js 14+ (App Router, Server Components & Client Islands).
- **Styling & Components:** Tailwind CSS, Shadcn UI, Radix Primitives, Lucide Icons.
- **Charts & Visualizations:** TradingView Lightweight Charts (financial candlestick), Recharts (sector heatmap & breadths).
- **State & Data Fetching:** TanStack React Query (auto-refresh, optimistic updates, request deduplication), Zustand (user watchlists & session state).

### 3.2 Page Blueprints
1. **Home & Market Dashboard (`/`):**
   - Live ticker bar (Nifty 50, Sensex, Bank Nifty, S&P 500).
   - Market regime gauge & Advance/Decline breadth meter.
   - Segmented Top Movers (Large, Mid, Small caps).
   - Interactive Sector Performance Heatmap.
   - Volume Shockers & 52-Week High/Low breakout alerts.
2. **IPO Intelligence Hub (`/ipos`):**
   - Active & Upcoming IPO list with price bands, issue dates, and subscription status.
   - Recently listed IPO performance tracker with post-listing return charts.
3. **Document Intelligence & RAG Chat (`/documents`):**
   - Drag-and-drop PDF filing uploader with progress tracking.
   - Split-screen UI: PDF viewer with highlighted citations on the left, interactive AI financial chat on the right.

---

## 4. Future Roadmap: Production Deployment & DevOps

### 4.1 Containerization (Docker)
- Multi-stage Dockerfile optimizing Python image size (< 500MB).
- Production ASGI runner via `uvicorn --workers 4 --proxy-headers`.

### 4.2 Cloud Infrastructure Plan
- **Backend Service:** AWS ECS (Fargate) or GCP Cloud Run for autoscaled, serverless container hosting.
- **Frontend App:** Vercel or AWS Amplify for edge-rendered Next.js hosting.
- **Database:** Managed PostgreSQL (AWS RDS or Supabase) with automated daily backups.
- **Vector Storage:** Persistent AWS EFS volume or Pinecone/Qdrant cloud cluster for production-scale FAISS/vector indexing.

### 4.3 CI/CD Automation (GitHub Actions)
- **CI Pipeline:** Automated linting (`ruff`), type checking (`mypy`), and test suite (`pytest`) on every pull request.
- **CD Pipeline:** On merge to `master`, build Docker container, push to AWS ECR, and trigger blue/green zero-downtime rolling deployment.
