from datetime import datetime, timedelta
import random

from fastapi.testclient import TestClient



def generate_user() -> dict:
    return {
        "username": f"test_username_{random.randint(100, 1000)}",
        "password": f"password{random.randint(100, 1000)}"
    }

def generate_category() -> dict:
    return {
        "category_name": f"name_{random.randint(100, 1000)}",
        "category_description": f"description_{random.randint(100, 1000)}",
        "category_type": random.choice(["expenses", "income"]),
    }

def generate_transaction(client: TestClient, category_id: str) -> dict:
    category: dict = client.get(f"api/v1/categories/{category_id}").json()
    transaction_value: float = round(random.uniform(0.01, 10000.00), 2)
    transaction_date: datetime = datetime.now() + timedelta(days=random.randint(-365, 365))

    return {
        "transaction_type": category["category_type"],
        "transaction_value": str(transaction_value),
        "transaction_date": transaction_date.isoformat(),
        "transaction_description": f"description_{random.randint(100, 1000)}",
        "category_id": category_id,
    }

def authorize(client: TestClient, user_data: dict) -> dict:
    return client.post("/api/v1/signin", data=user_data).json()

def get_user_id(client: TestClient, user_data: dict) -> str:
    token: dict = authorize(client, user_data)
    return client.get(
        "/api/v1/verify",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()["user_id"]

def get_category_id(client: TestClient, user_data: dict) -> str:
    token: dict = authorize(client, user_data)
    return client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()[0]["category_id"]

def get_transaction_id(client: TestClient, user_data: dict) -> str:
    token: dict = authorize(client, user_data)
    return client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()[0]["transaction_id"]


def test_root(client: TestClient) -> None:
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Initialized"}


def test_registration(client: TestClient) -> None:
    response = client.post("/api/v1/signup", json=generate_user())
    assert response.status_code == 201
    assert response.json()["access_token"] is not None

def test_authentication(client: TestClient, registered_test_user_data: dict) -> None:
    response = client.post("/api/v1/signin", data=registered_test_user_data)
    assert response.status_code == 200
    assert response.json()["access_token"] is not None

def test_verification(client: TestClient, registered_test_user_data: dict) -> None:
    token: dict = authorize(client, registered_test_user_data)
    response = client.get(
        "/api/v1/verify",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200

def test_edit_user(client: TestClient, registered_test_user_data: dict) -> None:
    new_user_data: dict = generate_user()
    new_user_data["old_password"] = "password123"
    new_user_data["new_password"] = new_user_data["password"]
    recover_user_data: dict = registered_test_user_data
    recover_user_data["old_password"] = new_user_data["new_password"]
    recover_user_data["new_password"] = new_user_data["old_password"]
    user_id: str = get_user_id(client, registered_test_user_data)

    response = client.patch(f"/api/v1/users/{user_id}", json=new_user_data)
    token = response.json()
    client.patch(f"/api/v1/users/{user_id}", json=recover_user_data)

    assert response.status_code == 200
    assert token["access_token"] is not None


def test_create_category(client: TestClient, registered_test_user_data: dict) -> None:
    token: dict = authorize(client, registered_test_user_data)
    response = client.post(
        "api/v1/categories",
        json=generate_category(),
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"},
    )
    assert response.status_code == 201

def test_get_categories(client: TestClient, registered_test_user_data: dict) -> None:
    token: dict = authorize(client, registered_test_user_data)
    response = client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200
    assert len(response.json()) == 1

def test_get_category(client: TestClient, registered_test_user_data: dict) -> None:
    category_id: str = get_category_id(client, registered_test_user_data)
    response = client.get(f"api/v1/categories/{category_id}")
    assert response.status_code == 200
    assert response.json() is not None

def test_edit_category(client: TestClient, registered_test_user_data: dict) -> None:
    category_id: str = get_category_id(client, registered_test_user_data)
    new_category: dict = generate_category()
    response = client.put(f"api/v1/categories/{category_id}", json=new_category)
    assert response.status_code == 200
    assert response.json()["category_name"] == new_category["category_name"]


def test_create_transaction(client: TestClient, registered_test_user_data: dict) -> None:
    token: dict = authorize(client, registered_test_user_data)
    category_id: str = get_category_id(client, registered_test_user_data)
    response = client.post(
        "api/v1/transactions",
        json=generate_transaction(client, category_id),
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"},
    )
    assert response.status_code == 201

def test_get_transactions(client: TestClient, registered_test_user_data: dict) -> None:
    token: dict = authorize(client, registered_test_user_data)
    response = client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    )
    assert response.status_code == 200
    assert len(response.json()) >= 0

def test_get_transaction(client: TestClient, registered_test_user_data: dict) -> None:
    transaction_id: str = get_transaction_id(client, registered_test_user_data)
    response = client.get(f"api/v1/transactions/{transaction_id}")
    assert response.status_code == 200
    assert response.json() is not None

def test_edit_transaction(client: TestClient, registered_test_user_data: dict) -> None:
    transaction_id: str = get_transaction_id(client, registered_test_user_data)
    category_id: str = get_category_id(client, registered_test_user_data)
    new_transaction: dict = generate_transaction(client, category_id)
    response = client.put(f"api/v1/transactions/{transaction_id}", json=new_transaction)
    assert response.status_code == 200
    assert response.json()["transaction_description"] == new_transaction["transaction_description"]

def test_delete_transaction(client: TestClient, registered_test_user_data: dict) -> None:
    token: dict = authorize(client, registered_test_user_data)
    transaction_id: str = get_transaction_id(client, registered_test_user_data)
    old_transaction_list: list = client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()
    response = client.delete(f"api/v1/transactions/{transaction_id}")
    new_transaction_list: list = client.get(
        "api/v1/transactions",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()
    assert response.status_code == 204
    assert len(old_transaction_list) - 1 == len(new_transaction_list)


def test_delete_category(client: TestClient, registered_test_user_data: dict) -> None:
    token: dict = authorize(client, registered_test_user_data)
    category_id: str = get_category_id(client, registered_test_user_data)
    old_category_list: list = client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()
    response = client.delete(f"api/v1/categories/{category_id}")
    new_category_list: list = client.get(
        "api/v1/categories",
        headers={"Authorization": f"{token["token_type"]} {token["access_token"]}"}
    ).json()
    assert response.status_code == 204
    assert len(old_category_list) - 1 == len(new_category_list)