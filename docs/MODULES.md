# MODULES

# Sprint 1 - Financial Document Intelligence

## Module 1 - PDF Upload & File Management

Status: Complete

Submodules - Upload - PDF signature and readability validation - 50 MB
streaming size limit - SQLite-backed metadata - Multiple PDF upload - List
documents - Delete document and stored file

## Module 2 - PDF Processing

Status: Complete

Submodules - Text extraction - Cleaning - Text-layout table detection -
Database persistence of parsed/cleaned text and detected tables
Deliverables - Parsed text - Clean document - Processing status

## Module 3 - RAG Indexing

Status: Complete

Dependencies: processed documents from Modules 1 and 2

Submodules - Page-aware chunking - Embeddings - FAISS - Database persistence
Deliverables - Searchable vector index with document/chunk/page storage -
Semantic search API with page citations

## Module 4 - Document Intelligence

Status: Planned

Submodules - Executive summary - SWOT - Financial metric extraction with
citations - Risks - Opportunities Deliverables - Stored AI report

## Module 5 - Recommendation Engine

Status: Planned

Submodules - Financial feature extraction - Rule-based scoring - Confidence
Deliverables - Buy/Hold/Sell - Reasons - Evidence citations - Disclaimer

## Module 6 - Multi Document Chat

Status: Planned

Submodules - Retriever - Prompt builder - Citation support - Multi-document
comparison Deliverables - Chat with one PDF - Chat with multiple PDFs -
Compare companies

==============================

# Sprint 2 - Market Intelligence

## Module 7 - Company Data

Status: Planned

Submodules - Company search - Financial statements - Ratios
Deliverables - Company dashboard

## Module 8 - News Engine

Status: Planned

Submodules - Google News RSS - Finnhub - Deduplication Deliverables -
Latest company news

## Module 9 - Sentiment Analysis

Status: Planned

Submodules - FinBERT - Aggregation Deliverables -
Positive/Negative/Neutral - Overall sentiment

## Module 10 - Recommendation

Status: Planned

Submodules - Financial score - Sentiment score - Final weighted score
Deliverables - Buy/Hold/Sell - Confidence - Explanation

## Module 11 - Company Chat

Status: Planned

Submodules - Context builder - Prompt templates - LLM Deliverables -
Chat using financial data + news

==============================

# Sprint 3 - Production

## Module 12 - Frontend

Status: Planned

Deliverables - Dashboard - Upload page - Company page - Chat UI

## Module 13 - Testing

Status: Planned

Deliverables - API tests - RAG evaluation - Sentiment validation

## Module 14 - Deployment

Status: Planned

Deliverables - Docker - Production deployment

==============================

# Final Deliverables

Financial Document Intelligence - Multiple PDF upload - Multi-PDF RAG -
AI summary - Financial extraction - SWOT - Buy/Hold/Sell - Chat - PDF
comparison

Market Intelligence - Stock search - Financial dashboard - News
aggregation - Sentiment analysis - Financial health score -
Buy/Hold/Sell - Company chat
