from fastapi.testclient import TestClient

from tests.utils import (
    authorize,
    generate_category,
    generate_transaction,
    get_last_category_id,
    get_last_transaction_id,
)


def test_create_transaction(
    client: TestClient,
    registered_test_user_data: dict[str, str],
) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    client.post("api/v1/categories", json=generate_category(), headers=headers)
    user_id: str = client.get(
        "api/v1/verify",
        headers=headers,
    ).json()["user_id"]
    category_id: str = get_last_category_id(client, registered_test_user_data)
    new_transaction = generate_transaction(client, category_id)
    old_list_of_transactions: list[dict[str, str]] = client.get(
        "api/v1/transactions",
        headers=headers,
    ).json()
    response = client.post(
        "api/v1/transactions",
        json=new_transaction,
        headers=headers,
    )
    new_list_of_transactions: list[dict[str, str | float]] = client.get(
        "api/v1/transactions",
        headers=headers,
    ).json()

    created_transaction: dict[str, str | float] = new_list_of_transactions[-1]
    created_transaction_id = created_transaction["transaction_id"]
    created_transaction_user_id = created_transaction["user_id"]
    transaction_creation_time = created_transaction["transaction_created"]
    del created_transaction["transaction_created"]
    del created_transaction["transaction_id"]
    del created_transaction["user_id"]

    assert response.status_code == 201
    assert len(old_list_of_transactions) + 1 == len(new_list_of_transactions)
    assert isinstance(created_transaction_id, str)
    assert len(created_transaction_id) == 36
    assert created_transaction_user_id == user_id
    assert created_transaction["category_id"] == category_id
    assert isinstance(transaction_creation_time, str)
    assert len(transaction_creation_time) == 27
    assert created_transaction == new_transaction


def test_get_transactions(
    client: TestClient,
    registered_test_user_data: dict[str, str],
) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    response = client.get(
        "api/v1/transactions",
        headers=headers,
    )

    assert response.status_code == 200


def test_get_transaction(client: TestClient, registered_test_user_data: dict) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    user_id: str = client.get(
        "api/v1/verify",
        headers=headers,
    ).json()["user_id"]

    transaction_id: str = get_last_transaction_id(client, registered_test_user_data)
    response = client.get(f"api/v1/transactions/{transaction_id}")
    transaction: dict[str, str | float] = response.json()

    assert response.status_code == 200
    assert transaction["transaction_type"] in ["income", "expenses"]
    assert isinstance(transaction["transaction_value"], float)
    assert isinstance(transaction["transaction_date"], str)
    assert len(transaction["transaction_date"]) == 27
    assert isinstance(transaction["transaction_created"], str)
    assert len(transaction["transaction_created"]) == 27
    assert isinstance(transaction["transaction_description"], str)
    assert isinstance(transaction["category_id"], str)
    assert len(transaction["category_id"]) == 36
    assert transaction["user_id"] == user_id


def test_edit_transaction(client: TestClient, registered_test_user_data: dict) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    transaction_id: str = get_last_transaction_id(client, registered_test_user_data)
    category_id: str = get_last_category_id(client, registered_test_user_data)
    old_transaction: dict[str, str | int] = client.get(
        f"api/v1/transactions/{transaction_id}", headers=headers
    ).json()
    new_transaction: dict = generate_transaction(client, category_id)
    response = client.put(f"api/v1/transactions/{transaction_id}", json=new_transaction)

    updated_transaction = response.json()

    assert response.status_code == 200
    assert updated_transaction["transaction_id"] == old_transaction["transaction_id"]
    assert (
        updated_transaction["transaction_type"] == new_transaction["transaction_type"]
    )
    assert (
        updated_transaction["transaction_value"] == new_transaction["transaction_value"]
    )
    assert (
        updated_transaction["transaction_date"] == new_transaction["transaction_date"]
    )
    assert (
        updated_transaction["transaction_created"]
        == old_transaction["transaction_created"]
    )
    assert (
        updated_transaction["transaction_description"]
        == new_transaction["transaction_description"]
    )
    assert updated_transaction["user_id"] == old_transaction["user_id"]
    assert updated_transaction["category_id"] == new_transaction["category_id"]


def test_delete_transaction(
    client: TestClient,
    registered_test_user_data: dict[str, str],
) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    transaction_id: str = get_last_transaction_id(client, registered_test_user_data)
    old_transaction_list: list[dict[str, str | float]] = client.get(
        "api/v1/transactions",
        headers=headers,
    ).json()
    response = client.delete(f"api/v1/transactions/{transaction_id}")
    new_transaction_list: list[dict[str, str | float]] = client.get(
        "api/v1/transactions",
        headers=headers,
    ).json()
    client.delete(
        f"api/v1/categories/{get_last_category_id(client, registered_test_user_data)}"
    )

    assert response.status_code == 204
    assert transaction_id not in [
        transaction["transaction_id"] for transaction in new_transaction_list
    ]
    assert len(old_transaction_list) - 1 == len(new_transaction_list)
