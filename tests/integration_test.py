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
def data():
    return {
        "user": {
            "username": "test_username",
            "password": "password123"
        },
        "new_user": {
            "username": "new_test_username",
            "old_password": "password123",
            "new_password": "password321"
        },
        "old_user": {
            "username": "test_username",
            "old_password": "password321",
            "new_password": "password123"
        },
        "category": {
            "category_name": "test category name",
            "category_description": "description",
            "category_type": "income",
        },
        "new_category": {
            "category_name": "new test category name",
            "category_description": "new description",
            "category_type": "expenses",
        },
    }

@pytest.fixture(scope="module")
def transaction_data(category_id):
    return {
        "transaction": {
            "transaction_type": "expenses",
            "transaction_value": "99.99",
            "transaction_date": "2032-04-23T10:20:30.400+02:30",
            "transaction_description": "description",
            "category_id": category_id,
        },
        "new transaction": {
            "transaction_type": "expenses",
            "transaction_value": "100",
            "transaction_date": "2032-04-23T10:20:30.400+02:30",
            "transaction_description": "new description",
            "category_id": category_id,
        },
    }

@pytest.fixture(scope="module")
def token(client, data):
    return client.post("/api/v1/signin", data=data["user"]).json()

@pytest.fixture(scope="module")
def user_id(client, token):
    return client.get(
        "/api/v1/verify",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()["user_id"]

@pytest.fixture(scope="module")
def category_id(client, token):
    return client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()[0]["category_id"]

@pytest.fixture(scope="module")
def transaction_id(client, token):
    return client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()[0]["transaction_id"]


def test_root(client: TestClient):
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Initialized"}


def test_registration(client: TestClient, data):
    response = client.post("/api/v1/signup", json=data["user"])
    assert response.status_code == 201
    assert response.json()["access_token"] is not None

def test_authentication(client: TestClient, data):
    response = client.post("/api/v1/signin", data=data["user"])
    assert response.status_code == 200
    assert response.json()["access_token"] is not None

def test_verification(client: TestClient, token):
    response = client.get(
        "/api/v1/verify",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200

def test_edit_user(client: TestClient, data, user_id):
    response = client.patch(f"/api/v1/users/{user_id}", json=data["new_user"])
    assert response.status_code == 200
    jwt = response.json()
    assert jwt["access_token"] is not None
    client.patch(f"/api/v1/users/{user_id}", json=data["old_user"])


def test_create_category(client: TestClient, data, token):
    response = client.post(
        "api/v1/categories",
        json=data["category"],
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"},
    )
    assert response.status_code == 201

def test_get_categories(client: TestClient, token):
    response = client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_category(client: TestClient, category_id):
    response = client.get(f"api/v1/categories/{category_id}")
    assert response.status_code == 200
    assert response.json() is not None

def test_edit_category(client: TestClient, data, category_id):
    response = client.put(f"api/v1/categories/{category_id}", json=data["new_category"])
    assert response.status_code == 200
    assert response.json()["category_name"] == "new test category name"


def test_create_transaction(client: TestClient, transaction_data, token):
    response = client.post(
        "api/v1/transactions",
        json=transaction_data["transaction"],
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"},
    )
    assert response.status_code == 201

def test_get_transactions(client: TestClient, token):
    response = client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 0

def test_get_transaction(client: TestClient, transaction_id):
    response = client.get(f"api/v1/transactions/{transaction_id}")
    assert response.status_code == 200
    assert response.json() is not None

def test_edit_transaction(client: TestClient, transaction_data, transaction_id):
    response = client.put(f"api/v1/transactions/{transaction_id}", json=transaction_data["new transaction"])
    assert response.status_code == 200
    assert response.json()["transaction_description"] == "new description"

def test_delete_transaction(client: TestClient, transaction_id, token):
    response = client.delete(f"api/v1/transactions/{transaction_id}")
    assert response.status_code == 204
    assert len(client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()) == 0


def test_delete_category(client: TestClient, category_id, token):
    response = client.delete(f"api/v1/categories/{category_id}")
    assert response.status_code == 204
    assert len(client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()) == 0