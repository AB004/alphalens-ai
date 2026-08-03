import os
from pathlib import Path

TEST_DATABASE = Path(__file__).parent / ".test_alphalens.db"
os.environ["DATABASE_URL"] = f"sqlite:///{TEST_DATABASE.as_posix()}"

import pytest
import numpy as np

from backend.database.session import Base, engine


@pytest.fixture(autouse=True)
def isolated_database_and_uploads(tmp_path, monkeypatch):
    from backend.services.pdf_processing import process_service
    from backend.services.pdf_upload import upload_service
    from backend.services.rag import index_service

    upload_dir = tmp_path / "uploads"
    monkeypatch.setattr(upload_service, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(process_service, "UPLOAD_DIR", upload_dir)
    monkeypatch.setattr(index_service, "INDEX_DIR", tmp_path / "indexes")

    class DeterministicEmbedder:
        model_name = "test-deterministic-embedder"

        def encode(self, texts):
            vectors = np.zeros((len(texts), 16), dtype=np.float32)
            for row, text in enumerate(texts):
                for character in text.lower():
                    vectors[row, ord(character) % 16] += 1
            return vectors

    monkeypatch.setattr(index_service, "get_embedder", lambda: DeterministicEmbedder())
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def pytest_sessionfinish(session, exitstatus):
    engine.dispose()
    TEST_DATABASE.unlink(missing_ok=True)
