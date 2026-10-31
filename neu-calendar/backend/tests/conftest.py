import sys
import os
from os.path import dirname, abspath

# Add backend directory to sys.path
backend_dir = dirname(dirname(abspath(__file__)))
sys.path.insert(0, backend_dir)

# Set testing environment variables before importing app modules
os.environ["ENVIRONMENT"] = "testing"
test_db_path = os.path.join(backend_dir, "test_neu.db")
os.environ["DATABASE_URL"] = f"sqlite:///{test_db_path}"

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from fastapi.testclient import TestClient

from app.core.database import Base, get_db
import app.core.database as db_module
from app.main import app

# Create SQLite engine with StaticPool or check_same_thread=False
test_engine = create_engine(
    f"sqlite:///{test_db_path}",
    connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=test_engine)

# Override engine and SessionLocal in db_module for tests
db_module.engine = test_engine
db_module.SessionLocal = TestingSessionLocal


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=test_engine)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture(scope="function")
def client(db):
    def override_get_db():
        try:
            yield db
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as test_client:
        yield test_client
    app.dependency_overrides.clear()


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    if os.path.exists(test_db_path):
        try:
            os.remove(test_db_path)
        except Exception:
            pass
