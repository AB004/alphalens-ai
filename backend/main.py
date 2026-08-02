from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.api.process import router as process_router
from backend.api.upload import router as upload_router
from backend.services.pdf_upload.upload_service import ensure_upload_dir
from database.models import Document
from database.session import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_upload_dir()
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(title="AlphaLens Document Intelligence API", version="0.2.0", lifespan=lifespan)
app.include_router(upload_router, prefix="/api")
app.include_router(process_router, prefix="/api")
