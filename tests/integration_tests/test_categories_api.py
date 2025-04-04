from fastapi.testclient import TestClient

from tests.utils import authorize, generate_category, get_category_id


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
    assert len(response.json()) >= 1

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