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
