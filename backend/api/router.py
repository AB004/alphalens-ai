from fastapi import APIRouter

from backend.api.documents.upload import router as upload_router
from backend.api.documents.processing import router as processing_router
from backend.api.documents.indexing import router as indexing_router
from backend.api.documents.search import router as search_router
from backend.api.documents.intelligence import (
    router as intelligence_router,
)
from backend.api.documents.recommendation import (
    router as recommendation_router,
)
from backend.api.documents.chat import (
    router as chat_router,
)
from backend.api.chat.conversation import (
    router as conversation_router,
)
from backend.api.chat.messages import (
    router as message_router,
)

api_router = APIRouter()

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
    recommendation_router,
    prefix="/documents",
    tags=["Recommendation"],
)

api_router.include_router(
    chat_router,
    prefix="/documents",
    tags=["Chat"],
)

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