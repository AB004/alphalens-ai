import os
from pathlib import Path

TEST_DATABASE = Path(__file__).parent / ".test_alphalens.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"

import pytest

from database.session import Base, engine


@pytest.fixture(autouse=True)
def isolated_database_and_uploads(tmp_path, monkeypatch):
    from backend.services.pdf_processing import process_service
    from backend.services.pdf_upload import upload_service

    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(upload_service, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(process_service, "UPLOAD_DIR", upload_dir)
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    TEST_DATABASE.unlink(missing_ok=True)
