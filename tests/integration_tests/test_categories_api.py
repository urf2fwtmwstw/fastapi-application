from fastapi.testclient import TestClient

from tests.utils import authorize, generate_category, get_last_category_id, get_user_id


def test_create_category(
    client: TestClient,
    registered_test_user_data: dict[str, str],
) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    user_id: str = get_user_id(client, registered_test_user_data)
    new_category = generate_category()
    old_list_of_categories: list[dict[str, str]] = client.get(
        "api/v1/categories",
        headers=headers,
    ).json()
    response = client.post(
        "api/v1/categories",
        json=new_category,
        headers=headers,
    )
    new_list_of_categories: list[dict[str, str]] = client.get(
        "api/v1/categories",
        headers=headers,
    ).json()
    created_category: dict[str, str] = new_list_of_categories[-1]
    created_category_id: str = created_category["category_id"]
    created_category_user_id: str = created_category["user_id"]
    del created_category["category_id"]
    del created_category["user_id"]

    assert response.status_code == 201
    assert len(old_list_of_categories) + 1 == len(new_list_of_categories)
    assert len(created_category_id) == 36
    assert created_category_user_id == user_id
    assert created_category == new_category


def test_get_categories(
    client: TestClient,
    registered_test_user_data: dict[str, str],
) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    response = client.get(
        "api/v1/categories",
        headers=headers,
    )

    assert response.status_code == 200
    assert len(response.json()) >= 1


def test_get_category(client: TestClient, registered_test_user_data: dict) -> None:
    category_id: str = get_last_category_id(client, registered_test_user_data)
    user_id: str = get_user_id(client, registered_test_user_data)
    response = client.get(f"api/v1/categories/{category_id}")
    category: dict[str, str] = response.json()

    assert response.status_code == 200
    assert isinstance(category["category_id"], str)
    assert len(category["category_id"]) == 36
    assert isinstance(category["category_name"], str)
    assert isinstance(category["category_description"], str)
    assert category["category_type"] in ["income", "expenses"]
    assert category["user_id"] == user_id


def test_edit_category(client: TestClient, registered_test_user_data: dict) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    user_id: str = get_user_id(client, registered_test_user_data)
    category_id: str = get_last_category_id(client, registered_test_user_data)
    old_category: dict[str, str] = client.get(
        f"api/v1/categories/{category_id}", headers=headers
    ).json()
    new_category: dict[str, str] = generate_category()
    response = client.put(f"api/v1/categories/{category_id}", json=new_category)
    updated_category: dict[str, str] = response.json()

    assert response.status_code == 200
    assert updated_category["category_id"] == old_category["category_id"]
    assert updated_category["category_name"] == new_category["category_name"]
    assert (
        updated_category["category_description"] == new_category["category_description"]
    )
    assert updated_category["category_type"] == new_category["category_type"]
    assert updated_category["user_id"] == user_id


def test_delete_category(
    client: TestClient,
    registered_test_user_data: dict[str, str],
) -> None:
    headers: dict[str, str] = authorize(client, registered_test_user_data)
    category_id: str = get_last_category_id(client, registered_test_user_data)
    old_category_list: list[dict[str, str]] = client.get(
        "api/v1/categories",
        headers=headers,
    ).json()
    response = client.delete(f"api/v1/categories/{category_id}")
    new_category_list: list[dict[str, str]] = client.get(
        "api/v1/categories",
        headers=headers,
    ).json()

    assert response.status_code == 204
    assert category_id not in [
        category["category_id"] for category in new_category_list
    ]
    assert len(old_category_list) - 1 == len(new_category_list)
