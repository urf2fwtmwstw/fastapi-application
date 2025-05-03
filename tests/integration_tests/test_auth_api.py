from fastapi.testclient import TestClient

from tests.utils import authorize, generate_user, get_user_id


def test_registration(client: TestClient) -> None:
    response = client.post("/api/v1/signup", json=generate_user())
    assert response.status_code == 201
    assert response.json()["access_token"] is not None


def test_authentication(client: TestClient, registered_test_user_data: dict) -> None:
    response = client.post("/api/v1/signin", data=registered_test_user_data)
    assert response.status_code == 200
    assert response.json()["access_token"] is not None


def test_verification(
    client: TestClient,
    registered_test_user_data: dict[str:str],
) -> None:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    response = client.get(
        "/api/v1/verify",
        headers=headers,
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
