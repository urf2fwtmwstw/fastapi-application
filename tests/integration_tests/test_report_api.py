from fastapi.testclient import TestClient

from tests.utils import (
    authorize,
    delete_test_data_for_reports,
    generate_test_data_for_report,
    get_expected_report_data,
    get_report_id,
)


def test_create_report(
    client: TestClient,
    registered_test_user_data: dict[str:str],
    report_data: dict[str:int],
) -> None:
    headers: dict[str:str] = authorize(client, registered_test_user_data)
    response = client.post(
        "api/v1/create_report",
        json=report_data,
        headers=headers,
    )
    assert response.status_code == 200
    assert response.json()["report_id"] is not None


def test_get_report(
    client: TestClient,
    registered_test_user_data: dict[str:str],
    report_data: dict[str:int],
) -> None:
    generate_test_data_for_report(client, registered_test_user_data)
    expected_report_data = get_expected_report_data(client, registered_test_user_data)
    report_id: str = get_report_id(client, registered_test_user_data, report_data)
    response = client.get(
        "api/v1/get_report",
        params={"report_id": report_id},
    )
    report = response.json()
    delete_test_data_for_reports(client, registered_test_user_data)
    assert response.status_code == 200
    assert report["month_income"] == expected_report_data["income"]
    assert report["month_expenses"] == expected_report_data["expenses"]
    assert report["balance"] == expected_report_data["balance"]
    assert (
        report["most_expensive_categories"]
        == expected_report_data["most_expensive_categories"]
    )
    assert report["status"] == "GENERATED"


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
    delete_test_data_for_reports(client, registered_test_user_data)
    assert response.status_code == 204
