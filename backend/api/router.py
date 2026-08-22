from fastapi import APIRouter


# ============================================================
# DOCUMENT APIs
# ============================================================

from backend.api.documents.upload import (
    router as upload_router,
)

from backend.api.documents.processing import (
    router as processing_router,
)

from backend.api.documents.indexing import (
    router as indexing_router,
)

from backend.api.documents.search import (
    router as search_router,
)

from backend.api.documents.intelligence import (
    router as intelligence_router,
)

from backend.api.documents.recommendation import (
    router as document_recommendation_router,
)

from backend.api.documents.chat import (
    router as chat_router,
)


# ============================================================
# CHAT APIs
# ============================================================

from backend.api.chat.conversation import (
    router as conversation_router,
)

from backend.api.chat.messages import (
    router as message_router,
)


# ============================================================
# COMPANY APIs
# ============================================================

from backend.api.company.company import (
    router as company_router,
)

from backend.api.company.news import (
    router as news_router,
)

from backend.api.company.recommendation import (
    router as market_recommendation_router,
)

from backend.api.company.company_chat import (
    router as company_chat_router,
)


# ============================================================
# SENTIMENT APIs
# ============================================================

from backend.api.sentiment.sentiment import (
    router as sentiment_router,
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
    market_recommendation_router,
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