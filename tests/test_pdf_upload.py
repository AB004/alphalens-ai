from fastapi.testclient import TestClient

from backend.main import app


SIMPLE_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 72 120 Td (Hello) Tj ET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000114 00000 n \n0000000230 00000 n \n0000000326 00000 n \ntrailer\n<< /Root 1 0 R /Size 6 >>\nstartxref\n383\n%%EOF"


def test_upload_single_pdf_persists_metadata():
    with TestClient(app) as client:
        response = client.post("/api/documents/upload", files=[("files", ("test.pdf", SIMPLE_PDF, "application/pdf"))])

        assert response.status_code == 201
        result = response.json()["uploads"][0]
        assert result["id"] > 0
        assert result["original_filename"] == "test.pdf"
        assert result["page_count"] == 1

        documents = client.get("/api/documents")
        assert documents.status_code == 200
        assert documents.json()["documents"][0]["id"] == result["id"]
        assert documents.json()["documents"][0]["status"] == "uploaded"


def test_upload_multiple_pdfs():
    with TestClient(app) as client:
        response = client.post("/api/upload", files=[
            ("files", ("first.pdf", SIMPLE_PDF, "application/pdf")),
            ("files", ("second.pdf", SIMPLE_PDF, "application/pdf")),
        ])

    assert response.status_code == 200
    assert [item["original_filename"] for item in response.json()["uploads"]] == ["first.pdf", "second.pdf"]


def test_upload_rejects_invalid_type_and_content():
    with TestClient(app) as client:
        wrong_extension = client.post("/api/upload", files=[("files", ("bad.txt", b"not a pdf", "text/plain"))])
        invalid_pdf = client.post("/api/upload", files=[("files", ("bad.pdf", b"%PDF-not-really-a-pdf", "application/pdf"))])

    assert wrong_extension.status_code == 400
    assert invalid_pdf.status_code == 400


def test_upload_enforces_size_limit(monkeypatch):
    from backend.services.pdf_upload import upload_service

    monkeypatch.setattr(upload_service, "MAX_FILE_SIZE", 20)
    with TestClient(app) as client:
        response = client.post("/api/upload", files=[("files", ("large.pdf", b"%PDF-" + b"x" * 20, "application/pdf"))])

    assert response.status_code == 413


def test_delete_document_removes_record_and_file():
    with TestClient(app) as client:
        uploaded = client.post("/api/upload", files=[("files", ("delete.pdf", SIMPLE_PDF, "application/pdf"))]).json()["uploads"][0]
        response = client.delete(f"/api/documents/{uploaded['id']}")

        assert response.status_code == 204
        assert client.get("/api/documents").json()["documents"] == []
