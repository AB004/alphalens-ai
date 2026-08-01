# AlphaLens Architecture

## Overview

AlphaLens consists of two independent AI systems sharing common
infrastructure.

    User
       |
    Frontend (Next.js)
       |
    Backend (FastAPI)
       |
    +---------------------------+
    |                           |
    | Financial Document AI     |
    | Market Intelligence AI    |
    +---------------------------+
                |
         Shared AI Layer
     (LLM, Embeddings, FAISS,
     Prompt Engine)

## Module 1 Pipeline

    Upload PDF
    ↓
    PyMuPDF
    ↓
    Text Cleaning
    ↓
    Chunking
    ↓
    Embeddings
    ↓
    FAISS
    ↓
    Retriever
    ↓
    Prompt Builder
    ↓
    Gemini
    ↓
    Answer

## Module 2 Pipeline

    Stock Symbol
    ↓
    yfinance
    ↓
    News RSS / Finnhub
    ↓
    FinBERT
    ↓
    Recommendation Engine
    ↓
    Prompt Builder
    ↓
    Gemini
    ↓
    Answer

## Shared Components

-   Embedding Model
-   FAISS
-   Gemini API
-   Prompt Templates
-   Logging
-   PostgreSQL
