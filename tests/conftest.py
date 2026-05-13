import os

os.environ.setdefault("POSTGRES_DSN", "sqlite+pysqlite:///:memory:")
os.environ.setdefault("UPLOAD_VOLUME_PATH", "./uploads-test")

import pytest
from fastapi.testclient import TestClient

from app.main import app
import app.routers.reviews as reviews_router
import app.routers.upload as upload_router


class FakeQueue:
    def enqueue(self, *args, **kwargs):
        return {"args": args, "kwargs": kwargs}


@pytest.fixture(autouse=True)
def patch_queue(monkeypatch):
    monkeypatch.setattr(upload_router, "get_queue", lambda: FakeQueue())
    monkeypatch.setattr(reviews_router, "get_queue", lambda: FakeQueue())


@pytest.fixture()
def client():
    with TestClient(app) as test_client:
        yield test_client
