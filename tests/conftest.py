import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine

from backend.database import session
from backend.main import app
from backend.seed import seed


@pytest.fixture()
def client(tmp_path):
    engine = create_engine(
        f"sqlite:///{tmp_path / 'test.db'}", connect_args={"check_same_thread": False}
    )
    seed(engine)
    from sqlalchemy.orm import Session

    def test_db():
        with Session(engine) as db:
            yield db

    app.dependency_overrides[session] = test_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()
    engine.dispose()
