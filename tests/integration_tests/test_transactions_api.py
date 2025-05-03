from fastapi.testclient import TestClient

from tests.utils import (
    authorize,
    generate_category,
    generate_transaction,
    get_category_id,
    get_transaction_id,
)


def test_create_transaction(
    client: TestClient,
    registered_test_user_data: dict[str:str],
) -> None:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    client.post("api/v1/categories", json=generate_category(), headers=headers)
    category_id: str = get_category_id(client, registered_test_user_data)
    response = client.post(
        "api/v1/transactions",
        json=generate_transaction(client, category_id),
        headers=headers,
    )
    assert response.status_code == 201


def test_get_transactions(
    client: TestClient,
    registered_test_user_data: dict[str:str],
) -> None:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    response = client.get(
        "api/v1/transactions",
        headers=headers,
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
    assert (
        response.json()["transaction_description"]
        == new_transaction["transaction_description"]
    )


def test_delete_transaction(
    client: TestClient,
    registered_test_user_data: dict[str:str],
) -> None:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    transaction_id: str = get_transaction_id(client, registered_test_user_data)
    old_transaction_list: list = client.get(
        "api/v1/transactions",
        headers=headers,
    ).json()
    response = client.delete(f"api/v1/transactions/{transaction_id}")
    new_transaction_list: list = client.get(
        "api/v1/transactions",
        headers=headers,
    ).json()
    client.delete(
        f"api/v1/categories/{get_category_id(client, registered_test_user_data)}"
    )
    assert response.status_code == 204
    assert len(old_transaction_list) - 1 == len(new_transaction_list)
