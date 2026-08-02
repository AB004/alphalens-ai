import os
from fastapi.testclient import TestClient
from backend.main import app
from backend.services.pdf_upload.upload_service import ensure_upload_dir

client = TestClient(app)
SIMPLE_PDF = b"%PDF-1.4\n1 0 obj\n<< /Type /Catalog /Pages 2 0 R >>\nendobj\n2 0 obj\n<< /Type /Pages /Kids [3 0 R] /Count 1 >>\nendobj\n3 0 obj\n<< /Type /Page /Parent 2 0 R /MediaBox [0 0 200 200] /Contents 4 0 R /Resources << /Font << /F1 5 0 R >> >> >>\nendobj\n4 0 obj\n<< /Length 44 >>\nstream\nBT /F1 24 Tf 72 120 Td (Hello) Tj ET\nendstream\nendobj\n5 0 obj\n<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>\nendobj\nxref\n0 6\n0000000000 65535 f \n0000000010 00000 n \n0000000061 00000 n \n0000000114 00000 n \n0000000230 00000 n \n0000000326 00000 n \ntrailer\n<< /Root 1 0 R /Size 6 >>\nstartxref\n383\n%%EOF"


def setup_upload_file(filename: str):
    ensure_upload_dir()
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "uploads")
    path = os.path.join(upload_dir, filename)
    with open(path, "wb") as f:
        f.write(SIMPLE_PDF)
    return filename


def cleanup_uploads():
    upload_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "backend", "uploads")
    if os.path.isdir(upload_dir):
        for filename in os.listdir(upload_dir):
            path = os.path.join(upload_dir, filename)
            if os.path.isfile(path):
                os.remove(path)


def test_process_single_pdf():
    cleanup_uploads()
    filename = setup_upload_file("process_test.pdf")
    response = client.post("/api/process", json={"filenames": [filename]})
    assert response.status_code == 200
    data = response.json()
    assert "processed" in data
    assert len(data["processed"]) == 1
    result = data["processed"][0]
    assert result["original_filename"] == filename
    assert result["stored_filename"] == filename
    assert result["page_count"] == 1
    assert "parsed_text" in result
    assert "clean_text" in result
    assert isinstance(result["tables"], list)


def test_process_missing_file():
    response = client.post("/api/process", json={"filenames": ["missing.pdf"]})
    assert response.status_code == 400
