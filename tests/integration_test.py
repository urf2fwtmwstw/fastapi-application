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
def user():
    return {"username": "test_username", "password": "password123"}

@pytest.fixture(scope="module")
def new_user():
    return {"username": "new_test_username", "old_password": "password123", "new_password": "password321"}

@pytest.fixture(scope="module")
def old_user():
    return {"username": "test_username", "old_password": "password321", "new_password": "password123"}

@pytest.fixture(scope="module")
def category():
    return {
                "category_name": "test category name",
                "category_description": "description",
                "category_type": "income",
            }

@pytest.fixture(scope="module")
def new_category():
    return {
                "category_name": "new test category name",
                "category_description": "new description",
                "category_type": "expenses",
            }

@pytest.fixture(scope="module")
def transaction(client, user):
    return {
                "transaction_type": "expenses",
                "transaction_value": "99.99",
                "transaction_date": "2032-04-23T10:20:30.400+02:30",
                "transaction_description": "description",
                "category_id": test_get_categories(client, user),
            }

@pytest.fixture(scope="module")
def new_transaction(client, user):
    return {
        "transaction_type": "expenses",
        "transaction_value": "100",
        "transaction_date": "2032-04-23T10:20:30.400+02:30",
        "transaction_description": "new description",
        "category_id": test_get_categories(client, user),
    }

def test_root(client: TestClient):
    response = client.get("/")
    data = response.json()
    assert response.status_code == 200
    assert data == {"message": "Initialized"}


def test_registration(client: TestClient, user):
    response = client.post("/api/v1/signup", json=user)
    assert response.status_code == 201
    assert response.json()["access_token"] is not None


def test_authentication(client: TestClient, user):
    response = client.post("/api/v1/signin", data=user)
    assert response.status_code == 200
    token = response.json()
    assert token["access_token"] is not None
    return token


def test_verification(client: TestClient, user):
    token = test_authentication(client, user)
    response = client.get("/api/v1/verify", headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"})
    assert response.status_code == 200
    user_data = response.json()
    return user_data["user_id"]


def test_edit_user(client: TestClient, new_user, old_user, user):
    user_id = test_verification(client, user)
    response = client.patch(f"/api/v1/users/{user_id}", json=new_user)
    assert response.status_code == 200
    token = response.json()
    assert token["access_token"] is not None
    client.patch(f"/api/v1/users{user_id}", json=old_user)


def test_create_category(client: TestClient, user, category):
    token = test_authentication(client, user)
    response = client.post(
        "api/v1/categories",
        json=category,
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 201


def test_get_categories(client: TestClient, user):
    token = test_authentication(client, user)
    response = client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200
    categories = response.json()
    assert len(categories) >= 0
    return categories[0]["category_id"]


def test_get_category(client: TestClient, user):
    category_id = test_get_categories(client, user)
    response = client.get(f"api/v1/categories/{category_id}")
    assert response.status_code == 200
    assert response.json() is not None


def test_edit_category(client: TestClient, new_category, user):
    category_id = test_get_categories(client, user)
    response = client.put(f"api/v1/categories/{category_id}", json=new_category)
    assert response.status_code == 200
    assert response.json()["category_name"] == "new test category name"


def test_create_transaction(client: TestClient, transaction, user):
    token = test_authentication(client, user)
    response = client.post(
        "api/v1/transactions/",
        json=transaction,
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 201


def test_get_transactions(client: TestClient, user):
    token = test_authentication(client, user)
    response = client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200
    transactions = response.json()
    assert len(transactions) >= 0
    return transactions[0]["transaction_id"]


def test_get_transaction(client: TestClient, user):
    transaction_id = test_get_transactions(client, user)
    response = client.get(f"api/v1/transactions/{transaction_id}")
    assert response.status_code == 200
    assert response.json() is not None


def test_edit_transaction(client: TestClient, new_transaction, user):
    transaction_id = test_get_transactions(client, user)
    response = client.put(f"api/v1/transactions/{transaction_id}", json=new_transaction)
    assert response.status_code == 200
    assert response.json()["transaction_description"] == "new description"


def test_delete_transaction(client: TestClient, user):
    transaction_id = test_get_transactions(client, user)
    response = client.delete(f"api/v1/transactions/{transaction_id}")
    assert response.status_code == 204


def test_delete_category(client: TestClient, user):
    category_id = test_get_categories(client, user)
    response = client.delete(f"api/v1/categories/{category_id}")
    assert response.status_code == 204