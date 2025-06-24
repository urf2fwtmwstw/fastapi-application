from unittest.mock import patch

import pytest
from fastapi.testclient import TestClient
from mockafka.admin_client import NewTopic
from mockafka.aiokafka import (
    FakeAIOKafkaAdmin,
    FakeAIOKafkaConsumer,
    FakeAIOKafkaProducer,
)

from internal.application.routers import handlers
from main import app


@pytest.fixture(scope="session")
def client():
    handlers(app)
    with TestClient(app) as client:
        yield client


@pytest.fixture(scope="session", autouse=True)
async def mock_kafka():
    admin = FakeAIOKafkaAdmin()
    await admin.create_topics(new_topics=[NewTopic(topic="report_tasks")])

    with (
        patch(
            "internal.transport.producer.producer.AIOKafkaProducer",
            FakeAIOKafkaProducer,
        ),
        patch(
            "internal.transport.consumer.consumer.AIOKafkaConsumer",
            FakeAIOKafkaConsumer,
        ),
    ):
        yield


@pytest.fixture(scope="module")
def registered_test_user_data():
    return {"username": "test_username", "password": "password123"}
