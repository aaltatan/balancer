from collections.abc import Callable, Generator
from typing import Any

import pytest
from app.api.dependencies.hash import get_hasher_fn, get_verifier_fn
from app.db import Base, get_db
from app.main import app
from fastapi.testclient import TestClient
from sqlalchemy import StaticPool, create_engine
from sqlalchemy.orm import Session, sessionmaker

engine = create_engine(
    "sqlite:///:memory:", connect_args={"check_same_thread": False}, poolclass=StaticPool
)
TestSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db() -> Generator[Session, Any, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


def override_hash_password(password: str) -> str:
    return f"hashed_{password}"


def override_verify_password(password: str, hashed_password: str) -> bool:
    return f"hashed_{password}" == hashed_password


app.dependency_overrides[get_db] = override_get_db
app.dependency_overrides[get_hasher_fn] = override_hash_password
app.dependency_overrides[get_verifier_fn] = override_verify_password


@pytest.fixture(scope="session")
def session() -> Generator[Session, Any, None]:
    db = TestSessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True, scope="session")
def init_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="session")
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture(scope="session")
def hasher_fn() -> Callable[[str], str]:
    return override_hash_password


@pytest.fixture(scope="session")
def verifier_fn() -> Callable[[str, str], bool]:
    return override_verify_password
