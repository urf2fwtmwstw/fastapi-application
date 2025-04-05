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