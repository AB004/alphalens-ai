import os
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

SIMPLE_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 72 120 Td (Hello) Tj ET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000114 00000 n \n0000000230 00000 n \n0000000326 00000 n \ntrailer\n<< /Root 1 0 R /Size 6 >>\nstartxref\n383\n%%EOF"


def cleanup_uploads():
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "uploads")
    if os.path.isdir(upload_dir):
        for filename in os.listdir(upload_dir):
            path = os.path.join(upload_dir, filename)
            if os.path.isfile(path):
                os.remove(path)


def test_upload_single_pdf():
    cleanup_uploads()
    response = client.post(
        "/api/upload",
        files=[("files", ("test.pdf", SIMPLE_PDF, "application/pdf"))],
    )
    assert response.status_code == 200
    data = response.json()
    assert "uploads" in data
    assert len(data["uploads"]) == 1
    result = data["uploads"][0]
    assert result["original_filename"] == "test.pdf"
    assert result["page_count"] == 1
    assert result["size_bytes"] > 0
    assert result["storage_path"].endswith("test.pdf")


def test_upload_multiple_pdfs():
    cleanup_uploads()
    response = client.post(
        "/api/upload",
        files=[
            ("files", ("first.pdf", SIMPLE_PDF, "application/pdf")),
            ("files", ("second.pdf", SIMPLE_PDF, "application/pdf")),
        ],
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data["uploads"]) == 2
    filenames = [item["original_filename"] for item in data["uploads"]]
    assert filenames == ["first.pdf", "second.pdf"]


def test_upload_invalid_file_type():
    response = client.post(
        "/api/upload",
        files=[("files", ("bad.txt", b"not a pdf", "text/plain"))],
    )
    assert response.status_code == 400
