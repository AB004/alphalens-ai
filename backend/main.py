from contextlib import asynccontextmanager

from fastapi import FastAPI
from backend.api.process import router as process_router
from backend.api.upload import router as upload_router
from backend.services.pdf_upload.upload_service import ensure_upload_dir


@asynccontextmanager
async def lifespan(app: FastAPI):
    ensure_upload_dir()
    yield


app = FastAPI(title="AlphaLens PDF Upload API", version="0.1.0", lifespan=lifespan)
app.include_router(upload_router, prefix="/api")
app.include_router(process_router, prefix="/api")
