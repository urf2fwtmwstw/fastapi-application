import random
from datetime import UTC, datetime, timedelta

from fastapi.testclient import TestClient


def generate_user() -> dict:
    return {
        "username": f"test_username_{random.randint(100, 1000)}",
        "password": f"password{random.randint(100, 1000)}",
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
    transaction_date: datetime = datetime.now() + timedelta(
        days=random.randint(-365, 365)
    )

    return {
        "transaction_type": category["category_type"],
        "transaction_value": str(transaction_value),
        "transaction_date": transaction_date.isoformat(),
        "transaction_description": f"description_{random.randint(100, 1000)}",
        "category_id": category_id,
    }


def authorize(client: TestClient, user_data: dict[str:str]) -> dict[str:str]:
    token = client.post("api/v1/signin", data=user_data).json()
    return {"Authorization": f"{token['token_type']} {token['access_token']}"}


def get_user_id(client: TestClient, user_data: dict[str:str]) -> str:
    headers: dict[str:str] = authorize(client, user_data)
    return client.get(
        "api/v1/verify",
        headers=headers,
    ).json()["user_id"]


def get_category_id(client: TestClient, user_data: dict) -> str:
    headers: dict[str:str] = authorize(client, user_data)
    return client.get(
        "api/v1/categories",
        headers=headers,
    ).json()[-1]["category_id"]


def get_transaction_id(client: TestClient, user_data: dict) -> str:
    headers: dict[str:str] = authorize(client, user_data)
    return client.get(
        "api/v1/transactions",
        headers=headers,
    ).json()[-1]["transaction_id"]


def get_report_id(
    client: TestClient,
    registered_test_user_data: dict[str:str],
    report_data: dict[str:int],
) -> str:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    return client.post(
        "api/v1/create_report",
        json=report_data,
        headers=headers,
    ).json()["report_id"]


def create_categories_for_report(
    client: TestClient,
    headers: dict[str:str],
) -> None:
    expenses_category: dict[str:str] = generate_category()
    expenses_category["category_type"] = "expenses"
    income_category: dict[str:str] = generate_category()
    income_category["category_type"] = "income"
    [
        client.post(
            "api/v1/categories",
            json=expenses_category,
            headers=headers,
        )
        for _ in range(6)
    ]
    client.post(
        "api/v1/categories",
        json=income_category,
        headers=headers,
    )


def create_transactions_for_report(
    client: TestClient,
    headers: dict[str:str],
) -> None:
    category_ids: list[str] = [
        category["category_id"]
        for category in client.get(
            "api/v1/categories",
            headers=headers,
        ).json()
    ]
    for category_id in category_ids:
        transaction = generate_transaction(client, category_id)
        transaction["transaction_date"] = datetime.now(tz=UTC).isoformat()
        client.post("api/v1/transactions", json=transaction, headers=headers)


def generate_test_data_for_report(
    client: TestClient,
    registered_test_user_data: dict[str:str],
) -> None:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    create_categories_for_report(client, headers)
    create_transactions_for_report(client, headers)


def get_expected_report_data(
    client: TestClient,
    registered_test_user_data: dict[str:str],
) -> dict[str : float | str : str]:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    total_transactions: list[dict[str : float | str : str]] = client.get(
        "api/v1/transactions", headers=headers
    ).json()
    expense_transactions: list[dict[str : float | str : str]] = [
        transaction
        for transaction in total_transactions
        if transaction["transaction_type"] == "expenses"
    ]
    income: float = 0
    expenses: float = 0
    balance: float = 0
    most_expensive_categories = ", ".join(
        [
            transaction["category_id"]
            for transaction in sorted(
                expense_transactions,
                key=lambda transaction: transaction["transaction_value"],
                reverse=True,
            )
        ][:5]
    )
    for transaction in total_transactions:
        match transaction["transaction_type"]:
            case "income":
                income += transaction["transaction_value"]
                balance += transaction["transaction_value"]
            case "expenses":
                expenses += transaction["transaction_value"]
                balance -= transaction["transaction_value"]
    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "balance": round(balance, 2),
        "most_expensive_categories": most_expensive_categories,
    }


def delete_test_data_for_reports(
    client: TestClient,
    registered_test_user_data: dict[str:str],
) -> None:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    transaction_ids: list[str] = [
        transaction["transaction_id"]
        for transaction in client.get(
            "api/v1/transactions",
            headers=headers,
        ).json()
    ]
    [
        client.delete(f"api/v1/transactions/{transaction_id}", headers=headers)
        for transaction_id in transaction_ids
    ]
    category_ids: list[str] = [
        category["category_id"]
        for category in client.get(
            "api/v1/categories",
            headers=headers,
        ).json()
    ]
    [
        client.delete(f"api/v1/categories/{category_id}", headers=headers)
        for category_id in category_ids
    ]
