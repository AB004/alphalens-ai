from fastapi import APIRouter


# ============================================================
# DOCUMENT APIs
# ============================================================

from backend.api.documents.upload import (
    router as upload_router,
)

from backend.api.documents.document_processing import (
    router as processing_router,
)

from backend.api.documents.document_indexing import (
    router as indexing_router,
)

from backend.api.documents.search import (
    router as search_router,
)

from backend.api.documents.document_intelligence import (
    router as intelligence_router,
)

from backend.api.documents.document_recommendations import (
    router as document_recommendation_router,
)

from backend.api.documents.document_chat import (
    router as chat_router,
)


# ============================================================
# CHAT APIs
# ============================================================

from backend.api.document_chat.document_conversations import (
    router as conversation_router,
)

from backend.api.document_chat.document_messages import (
    router as message_router,
)


# ============================================================
# COMPANY APIs
# ============================================================

from backend.api.company.companies import (
    router as company_router,
)

from backend.api.company.company_news import (
    router as news_router,
)

from backend.api.company.market_recommendations import (
    router as company_recommendation_router,
)

from backend.api.company.company_chat import (
    router as company_chat_router,
)


# ============================================================
# SENTIMENT APIs
# ============================================================

from backend.api.sentiment.sentiment_analysis import (
    router as sentiment_router,
)


# ============================================================
# HOME & MARKET OVERVIEW APIs (MODULE 11.5)
# ============================================================

from backend.api.home.home import (
    router as home_router,
)


api_router = APIRouter()


# ============================================================
# DOCUMENT APIs
# ============================================================

api_router.include_router(
    upload_router,
    prefix="/documents",
    tags=["Documents"],
)

api_router.include_router(
    processing_router,
    prefix="/documents",
    tags=["Processing"],
)

api_router.include_router(
    indexing_router,
    prefix="/documents",
    tags=["Indexing"],
)

api_router.include_router(
    search_router,
    prefix="/documents",
    tags=["Search"],
)

api_router.include_router(
    intelligence_router,
    prefix="/documents",
    tags=["Document Intelligence"],
)

api_router.include_router(
    document_recommendation_router,
    prefix="/documents",
    tags=["Recommendation"],
)

api_router.include_router(
    chat_router,
    prefix="/documents",
    tags=["Chat"],
)


# ============================================================
# CONVERSATION APIs
# ============================================================

api_router.include_router(
    conversation_router,
    prefix="/chat",
    tags=["Conversation"],
)

api_router.include_router(
    message_router,
    prefix="/chat",
    tags=["Messages"],
)


# ============================================================
# COMPANY APIs
# ============================================================

api_router.include_router(
    company_router,
    prefix="/company",
    tags=["Company"],
)

api_router.include_router(
    news_router,
    prefix="/company",
    tags=["Company News"],
)

api_router.include_router(
    company_recommendation_router,
    prefix="/company",
    tags=["Market Recommendation"],
)

api_router.include_router(
    company_chat_router,
    prefix="/company",
    tags=["Company Chat"],
)


# ============================================================
# SENTIMENT APIs
# ============================================================

api_router.include_router(
    sentiment_router,
    prefix="/sentiment",
    tags=["Sentiment"],
)


# ============================================================
# HOME & MARKET OVERVIEW APIs (MODULE 11.5)
# ============================================================

api_router.include_router(
    home_router,
    prefix="/home",
    tags=["Home & Market Overview"],
)

api_router.include_router(
    home_router,
    prefix="/market",
    tags=["Home & Market Overview"],
)