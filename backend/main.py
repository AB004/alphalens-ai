from contextlib import asynccontextmanager

from fastapi import FastAPI

from backend.api.router import api_router
from backend.database.session import Base,engine
import backend.models  # Registers all models
from backend.services.pdf_upload.upload_service import ensure_upload_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_upload_dir()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AlphaLens Document Intelligence API",
    version="0.2.0",
    lifespan=lifespan,
)

app.include_router(api_router, prefix="/api")