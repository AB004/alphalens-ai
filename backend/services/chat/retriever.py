from pathlib import Path

import faiss
import numpy as np
from fastapi import HTTPException, status

from backend.database.session import SessionLocal
from backend.repositories.chunk_repository import get_chunks_for_document
from backend.repositories.document_repository import get_document
from backend.repositories.index_repository import get_document_index
from backend.services.rag.index_service import get_embedder


class Retriever:

    def __init__(self):
        self.embedder = get_embedder()

    def _search_document(
        self,
        db,
        document_id: int,
        query_vector: np.ndarray,
        top_k: int,
    ) -> list[dict]:

        document = get_document(
            db,
            document_id,
        )

        if document is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Document {document_id} not found.",
            )

        document_index = get_document_index(
            db,
            document_id,
        )

        if document_index is None:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=f"Document {document_id} is not indexed.",
            )

        index_path = Path(document_index.index_path)

        if not index_path.exists():
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"FAISS index not found for document {document_id}.",
            )

        index = faiss.read_index(str(index_path))

        scores, vector_ids = index.search(
            query_vector,
            min(top_k, document_index.chunk_count),
        )

        chunk_lookup = {
            chunk.faiss_vector_id: chunk
            for chunk in get_chunks_for_document(
                db,
                document_id,
            )
        }

        results = []

        for score, vector_id in zip(
            scores[0],
            vector_ids[0],
        ):

            if vector_id == -1:
                continue

            chunk = chunk_lookup.get(int(vector_id))

            if chunk is None:
                continue

            results.append(
                {
                    "document_id": document_id,
                    "document_name": document.original_filename,
                    "chunk_id": chunk.id,
                    "chunk_index": chunk.chunk_index,
                    "page_number": chunk.page_number,
                    "text": chunk.text,
                    "score": float(score),
                }
            )

        return results

    def retrieve(
        self,
        document_ids: list[int],
        query: str,
        top_k: int = 10,
    ) -> list[dict]:

        if not document_ids:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="No document ids supplied.",
            )

        db = SessionLocal()

        try:

            query_vector = self.embedder.encode(
                [query]
            )

            faiss.normalize_L2(query_vector)

            all_results = []

            for document_id in document_ids:

                all_results.extend(
                    self._search_document(
                        db=db,
                        document_id=document_id,
                        query_vector=query_vector,
                        top_k=top_k,
                    )
                )

            all_results.sort(
                key=lambda chunk: chunk["score"],
                reverse=True,
            )

            return all_results[:top_k]

        finally:
            db.close()


retriever = Retriever()