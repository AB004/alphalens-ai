from pathlib import Path

from fastapi.testclient import TestClient

from backend.main import app
from tests.test_pdf_upload import SIMPLE_PDF


def test_process_document_by_id_persists_clean_text():
    with TestClient(app) as client:
        uploaded = client.post("/api/upload", files=[("files", ("process.pdf", SIMPLE_PDF, "application/pdf"))]).json()["uploads"][0]
        response = client.post("/api/process", json={"document_ids": [uploaded["id"]]})

        assert response.status_code == 200
        result = response.json()["processed"][0]
        assert result["id"] == uploaded["id"]
        assert result["original_filename"] == "process.pdf"
        assert result["page_count"] == 1
        assert "Hello" in result["clean_text"]
        assert client.get("/api/documents").json()["documents"][0]["status"] == "processed"


def test_process_missing_document_returns_404():
    with TestClient(app) as client:
        response = client.post("/api/process", json={"document_ids": [999]})
    assert response.status_code == 404


def test_infosys_report_end_to_end():
    report_path = Path(__file__).parent / "infosys-ar-26.pdf"
    with report_path.open("rb") as report, TestClient(app) as client:
        uploaded = client.post("/api/documents/upload", files=[("files", (report_path.name, report, "application/pdf"))])
        assert uploaded.status_code == 201
        document = uploaded.json()["uploads"][0]
        processed = client.post("/api/process", json={"document_ids": [document["id"]]})

    assert processed.status_code == 200
    result = processed.json()["processed"][0]
    assert result["page_count"] == 383
    assert len(result["parsed_text"]) > 1_000_000
    assert len(result["clean_text"]) > 1_000_000
    assert result["tables"]
