import os
from pathlib import Path
from typing import Protocol

import faiss
import numpy as np
from fastapi import HTTPException, status
from pypdf import PdfReader
from sqlalchemy.exc import SQLAlchemyError

from backend.services.pdf_processing.process_service import clean_extracted_text
from backend.repositories.document_repository import (
    get_document,
)
from backend.repositories.chunk_repository import (
    get_chunks_for_document,
)
from backend.repositories.index_repository import (
    get_document_index,
    replace_document_index,
    delete_document_index,
)
from backend.database.session import SessionLocal


INDEX_DIR = Path(__file__).resolve().parents[2] / "indexes"
DEFAULT_EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")


class Embedder(Protocol):
    model_name: str

    def encode(self, texts: list[str]) -> np.ndarray: ...


class SentenceTransformerEmbedder:
    def __init__(self, model_name: str = DEFAULT_EMBEDDING_MODEL):
        self.model_name = model_name
        try:
            from sentence_transformers import SentenceTransformer
        except ImportError as exc:
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Embedding dependency is unavailable. Install sentence-transformers.",
            ) from exc
        self._model = SentenceTransformer(model_name)

    def encode(self, texts: list[str]) -> np.ndarray:
        vectors = self._model.encode(texts, normalize_embeddings=True, show_progress_bar=False)
        return np.asarray(vectors, dtype=np.float32)


_embedder: Embedder | None = None


def get_embedder() -> Embedder:
    global _embedder
    if _embedder is None:
        _embedder = SentenceTransformerEmbedder()
    return _embedder


def ensure_index_dir() -> None:
    INDEX_DIR.mkdir(parents=True, exist_ok=True)


def _split_text(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    chunks = []
    start = 0
    text = text.strip()
    while start < len(text):
        end = min(start + chunk_size, len(text))
        if end < len(text):
            break_at = text.rfind(" ", start, end)
            if break_at > start + chunk_size // 2:
                end = break_at
        chunk = text[start:end].strip()
        if chunk:
            chunks.append(chunk)
        if end >= len(text):
            break
        start = max(end - chunk_overlap, start + 1)
    return chunks


def create_page_aware_chunks(pdf_path: Path, chunk_size: int, chunk_overlap: int) -> list[dict]:
    try:
        reader = PdfReader(str(pdf_path))
        chunks = []
        chunk_index = 0
        for page_number, page in enumerate(reader.pages, start=1):
            clean_page_text = clean_extracted_text(page.extract_text() or "")
            for text in _split_text(clean_page_text, chunk_size, chunk_overlap):
                chunks.append({"chunk_index": chunk_index, "page_number": page_number, "text": text})
                chunk_index += 1
        return chunks
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Unable to create document chunks: {exc}") from exc


def _index_path(document_id: int) -> Path:
    return INDEX_DIR / f"document_{document_id}.faiss"


def _serialize_index(document_id: int, document_index) -> dict:
    return {
        "document_id": document_id,
        "status": "indexed",
        "chunk_count": document_index.chunk_count,
        "vector_dimension": document_index.vector_dimension,
        "embedding_model": document_index.embedding_model,
        "indexed_at": document_index.indexed_at,
    }


def create_document_index(document_id: int, chunk_size: int, chunk_overlap: int) -> dict:
    if chunk_overlap >= chunk_size:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="chunk_overlap must be smaller than chunk_size.")

    db = SessionLocal()
    try:
        document = get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_id}")
        if document.status not in {"processed", "indexed"}:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Process the document before indexing it.")

        chunks = create_page_aware_chunks(Path(document.storage_path), chunk_size, chunk_overlap)
        if not chunks:
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="No extractable text was found to index.")

        embedder = get_embedder()
        vectors = embedder.encode([chunk["text"] for chunk in chunks])
        if vectors.ndim != 2 or vectors.shape[0] != len(chunks):
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Embedding model returned invalid vectors.")
        faiss.normalize_L2(vectors)

        ensure_index_dir()
        index_path = _index_path(document_id)
        temp_path = index_path.with_suffix(".faiss.tmp")
        vector_index = faiss.IndexFlatIP(vectors.shape[1])
        vector_index.add(vectors)
        faiss.write_index(vector_index, str(temp_path))
        os.replace(temp_path, index_path)

        for vector_id, chunk in enumerate(chunks):
            chunk["faiss_vector_id"] = vector_id
        document_index = replace_document_index(
            db,
            document,
            {
                "index_path": str(index_path),
                "embedding_model": embedder.model_name,
                "vector_dimension": int(vectors.shape[1]),
                "chunk_count": len(chunks),
            },
            chunks,
        )
        document.status = "indexed"
        db.commit()
        db.refresh(document_index)
        return _serialize_index(document_id, document_index)
    except SQLAlchemyError as exc:
        db.rollback()
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Unable to persist document index metadata.") from exc
    finally:
        db.close()


def search_document(document_id: int, query: str, top_k: int) -> dict:
    db = SessionLocal()
    try:
        document = get_document(db, document_id)
        if not document:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"Document not found: {document_id}")
        document_index = get_document_index(db, document_id)
        if not document_index or not Path(document_index.index_path).is_file():
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Index the document before searching it.")

        query_vector = get_embedder().encode([query])
        if query_vector.ndim != 2 or query_vector.shape[1] != document_index.vector_dimension:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Embedding model does not match the stored index.")
        faiss.normalize_L2(query_vector)
        vector_index = faiss.read_index(document_index.index_path)
        scores, vector_ids = vector_index.search(query_vector, min(top_k, document_index.chunk_count))
        chunks_by_vector_id = {chunk.faiss_vector_id: chunk for chunk in get_chunks_for_document(db, document_id)}
        results = []
        for score, vector_id in zip(scores[0], vector_ids[0]):
            chunk = chunks_by_vector_id.get(int(vector_id))
            if chunk:
                results.append(
                    {
                        "chunk_id": chunk.id,
                        "chunk_index": chunk.chunk_index,
                        "page_number": chunk.page_number,
                        "text": chunk.text,
                        "score": float(score),
                    }
                )
        return {"document_id": document_id, "query": query, "results": results}
    finally:
        db.close()


def remove_document_index(document_id: int) -> None:
    db = SessionLocal()
    try:
        document_index = delete_document_index(db, document_id)
        if document_index:
            Path(document_index.index_path).unlink(missing_ok=True)
    finally:
        db.close()
