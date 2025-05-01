from fastapi.testclient import TestClient

from tests.utils import authorize, get_report_id


def test_create_report(
    client: TestClient,
    registered_test_user_data: dict[str:str],
    report_data: dict[str:int],
) -> None:
    token: dict = authorize(client, registered_test_user_data)
    response = client.post(
        "api/v1/create_report",
        json=report_data,
        headers={"Authorization": f"{token['token_type']} {token['access_token']}"},
    )
    assert response.status_code == 200
    assert response.json()["report_id"] is not None


def test_get_report(
    client: TestClient,
    registered_test_user_data: dict[str:str],
    report_data: dict[str:int],
) -> None:
    report_id: str = get_report_id(client, registered_test_user_data, report_data)
    response = client.get(
        "api/v1/get_report",
        params={"report_id": report_id},
    )
    assert response.status_code == 200
    assert response.json() is not None


def test_delete_report(
    client: TestClient,
    registered_test_user_data: dict[str:str],
    report_data: dict[str:int],
) -> None:
    report_id: str = get_report_id(client, registered_test_user_data, report_data)
    response = client.delete(
        "api/v1/delete_report",
        params={"report_id": report_id},
    )
    assert response.status_code == 204
