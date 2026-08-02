from fastapi.testclient import TestClient

from backend.main import app
from tests.test_pdf_upload import SIMPLE_PDF


def upload_and_process_document(client: TestClient) -> int:
    uploaded = client.post("/api/upload", files=[("files", ("rag.pdf", SIMPLE_PDF, "application/pdf"))])
    assert uploaded.status_code == 200
    document_id = uploaded.json()["uploads"][0]["id"]
    processed = client.post("/api/process", json={"document_ids": [document_id]})
    assert processed.status_code == 200
    return document_id


def test_index_and_search_processed_document():
    with TestClient(app) as client:
        document_id = upload_and_process_document(client)
        indexed = client.post(f"/api/documents/{document_id}/index", json={"chunk_size": 300, "chunk_overlap": 50})

        assert indexed.status_code == 200
        index_result = indexed.json()
        assert index_result["status"] == "indexed"
        assert index_result["chunk_count"] == 1
        assert index_result["embedding_model"] == "test-deterministic-embedder"

        searched = client.post(f"/api/documents/{document_id}/search", json={"query": "Hello", "top_k": 5})
        assert searched.status_code == 200
        result = searched.json()["results"][0]
        assert result["page_number"] == 1
        assert "Hello" in result["text"]

        document = client.get("/api/documents").json()["documents"][0]
        assert document["status"] == "indexed"


def test_index_requires_processed_document():
    with TestClient(app) as client:
        uploaded = client.post("/api/upload", files=[("files", ("not-processed.pdf", SIMPLE_PDF, "application/pdf"))])
        document_id = uploaded.json()["uploads"][0]["id"]
        response = client.post(f"/api/documents/{document_id}/index", json={})

    assert response.status_code == 409


def test_search_requires_index():
    with TestClient(app) as client:
        document_id = upload_and_process_document(client)
        response = client.post(f"/api/documents/{document_id}/search", json={"query": "Hello"})

    assert response.status_code == 409
