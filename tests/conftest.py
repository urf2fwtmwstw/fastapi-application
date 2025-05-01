import pytest
from fastapi.testclient import TestClient

from internal.application.routers import handlers
from main import app


@pytest.fixture(scope="session")
def client():
    handlers(app)
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="module")
def registered_test_user_data():
    return {"username": "test_username", "password": "password123"}


@pytest.fixture(scope="module")
def report_data() -> dict[str:int]:
    return {"report_year": 2025, "report_month": 4}
