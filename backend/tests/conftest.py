import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.database import Base, get_db  # noqa: E402
from app.demo_seed import seed_demo_data  # noqa: E402
from app.main import app  # noqa: E402


@pytest.fixture
def session(tmp_path: Path) -> Session:
    database_file = tmp_path / "test_visa_sponsor_jobs.db"
    engine = create_engine(f"sqlite:///{database_file.as_posix()}", connect_args={"check_same_thread": False})
    TestingSessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False, future=True)
    Base.metadata.create_all(bind=engine)
    with TestingSessionLocal() as db:
        yield db
    engine.dispose()


@pytest.fixture
def seeded_session(session: Session) -> Session:
    seed_demo_data(session)
    return session


@pytest.fixture
def client(seeded_session: Session) -> TestClient:
    def override_get_db():
        yield seeded_session

    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    test_client.close()
    app.dependency_overrides.clear()
