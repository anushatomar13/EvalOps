import os
import tempfile

# Configure an isolated test database BEFORE importing the app, so the engine
# and settings are built against it.
_tmp = tempfile.NamedTemporaryFile(suffix=".db", delete=False)
_tmp.close()
os.environ["DATABASE_URL"] = f"sqlite:///{_tmp.name}"
os.environ["REDIS_URL"] = ""  # eager Celery

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from app.core.db import Base, engine  # noqa: E402
import app.models  # noqa: E402,F401
from app.main import app  # noqa: E402


@pytest.fixture(scope="session", autouse=True)
def _create_schema():
    Base.metadata.create_all(bind=engine)
    yield
    os.unlink(_tmp.name)


@pytest.fixture()
def client():
    with TestClient(app) as c:
        yield c
