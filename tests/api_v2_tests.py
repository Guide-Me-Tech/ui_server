import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import unittest
from fastapi.testclient import TestClient
from src.server import app
import httpx


@pytest.fixture
def client():
    return TestClient(app, base_url="http://localhost:8003")


# BASE_URL = "http://localhost:8003"


# @pytest.fixture
# def client():
#     return httpx.Client(base_url=BASE_URL, timeout=10.0)


def test_get_balance(client):
    response = client.post(
        "/chat/v2/build_ui/actions",
        json={
            "function_name": "get_balance",
            "llm_output": "Test LLM output",
            "backend_output": [
                {
                    "pan": "1234",
                    "image_url": "https://example.com/image.png",
                    "processingSystem": "Uzcard",
                    "balance": 1000,
                    "cardDetails": {
                        "cardName": "Test Card",
                        "cardColor": "#FFFFFF",
                    },
                },
                {
                    "pan": "1234",
                    "image_url": "https://example.com/image.png",
                    "processingSystem": "VISA",
                    "balance": 2000,
                    "cardDetails": {
                        "cardName": "Test Card",
                        "cardColor": "#FFFFFF",
                    },
                },
                {
                    "pan": "1234",
                    "image_url": "https://example.com/image.png",
                    "processingSystem": "Humo",
                    "balance": 3000,
                    "cardDetails": {
                        "cardName": "Test Card",
                        "cardColor": "#FFFFFF",
                    },
                },
            ],
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" not in str(response.json())


def test_get_categories(client):
    response = client.post(
        "/chat/v2/build_ui/actions",
        json={
            "function_name": "get_categories",
            "llm_output": "Test LLM output",
            "backend_output": [
                {
                    "id": 1,
                    "name": "Мобильные операторы",
                    "imagePath": None,
                    "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056545-57d63349-cdc1-4438-982f-23ae508dd782",
                },
                {
                    "id": 2,
                    "name": "Мобильные операторы",
                    "imagePath": None,
                    "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056545-57d63349-cdc1-4438-982f-23ae508dd782",
                },
                {
                    "id": 3,
                    "name": "Мобильные операторы",
                    "imagePath": None,
                    "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056545-57d63349-cdc1-4438-982f-23ae508dd782",
                },
            ],
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" not in str(response.json())


def test_get_fields_of_supplier(client):
    response = client.post(
        "/chat/v2/build_ui/actions",
        json={
            "function_name": "get_fields_of_supplier",
            "llm_output": "Test LLM output",
            "backend_output": {
                "fieldList": [
                    {
                        "identName": "amount",
                        "name": "Сумма",
                        "order": 2,
                        "type": "MONEY",
                        "pattern": None,
                        "minValue": 500,
                        "maxValue": 10000000,
                        "fieldSize": 12,
                        "isMain": None,
                        "valueList": [],
                    },
                    {
                        "identName": "paymentNo",
                        "name": "Номер счёта",
                        "order": 1,
                        "type": "STRING",
                        "pattern": None,
                        "minValue": None,
                        "maxValue": None,
                        "fieldSize": 15,
                        "isMain": True,
                        "valueList": [],
                    },
                ]
            },
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" not in str(response.json())


def test_get_suppliers_by_category(client):
    response = client.post(
        "/chat/v2/build_ui/actions",
        json={
            "function_name": "get_suppliers_by_category",
            "llm_output": "Test LLM output",
            "backend_output": [
                {
                    "id": 1014,
                    "name": "Crediton.uz",
                    "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671093787-252daee5-82ac-4fb4-ba5c-03787fe386f8",
                },
                {
                    "id": 1015,
                    "name": "Crediton.uz",
                    "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671093787-252daee5-82ac-4fb4-ba5c-03787fe386f8",
                },
                {
                    "id": 1016,
                    "name": "Crediton.uz",
                    "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671093787-252daee5-82ac-4fb4-ba5c-03787fe386f8",
                },
                {
                    "id": 1017,
                    "name": "Crediton.uz",
                    "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671093787-252daee5-82ac-4fb4-ba5c-03787fe386f8",
                },
            ],
        },
    )
    print("Response: ", response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" not in str(response.json())


def test_chatbot_answer(client):
    response = client.post(
        "/chat/v2/build_ui/actions",
        json={
            "function_name": "chatbot_answer",
            "llm_output": "Test LLM output",
            "backend_output": {},
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" not in str(response.json())


# def test_get_receiver_id_by_reciver_phone_number(self):
#     response = self.client.post(
#         "/chat/v2/build_ui/actions",
#         json={
#             "function_name": "get_receiver_id_by_reciver_phone_number",
#             "llm_output": "Test LLM output",
#             "backend_output": {
#                 "receiver_id": "1234",
#                 "receiver_name": "Test Name",
#             },
#         },
#     )
#     print(response.json())
#     self.assertEqual(response.status_code, 200)
#     self.assertIn("widgets", response.json())


# def test_invalid_function_name(self):
#     response = self.client.post(
#         "/chat/v2/build_ui/actions",
