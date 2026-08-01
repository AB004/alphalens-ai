# AlphaLens

## AI Financial Research Platform

AlphaLens is a solo AI project built to learn modern AI application
development.

It consists of two independent AI products:

## Product A -- Financial Document Intelligence

Upload one or more financial PDFs and: - Summarize documents - Extract
financial metrics - Detect risks & opportunities - Generate SWOT -
Explainable Buy / Hold / Sell - Chat with single or multiple PDFs
(RAG) - Compare companies across reports

### AI Pipeline

PDF -\> Parse -\> Chunk -\> Embeddings -\> FAISS -\> Retriever -\> LLM
-\> Answer

------------------------------------------------------------------------

## Product B -- Market Intelligence

Enter a stock symbol and: - Fetch company financials - Collect latest
news - Perform sentiment analysis - Generate financial health score -
Explainable Buy / Hold / Sell - Chat about the company using retrieved
data

### AI Pipeline

Stock -\> Financial APIs -\> News -\> Sentiment -\> Recommendation -\>
LLM

## Tech Stack

Frontend: - Next.js - Tailwind CSS

Backend: - FastAPI - PostgreSQL

AI: - Gemini API - SentenceTransformers - FAISS - FinBERT

Data Sources: - yfinance - Google News RSS - Finnhub (Free)

Deployment: - Docker

## Learning Goals

-   RAG
-   Embeddings
-   Vector Search
-   Prompt Engineering
-   Sentiment Analysis
-   Information Extraction
-   Recommendation Engine
-   Full-stack AI Application Development
