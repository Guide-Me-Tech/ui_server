import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
import unittest
from fastapi.testclient import TestClient
from src.server import app


@pytest.fixture
def client():
    return TestClient(app)


def test_get_notifications(client):
    response = client.post(
        "/chat/v3/build_ui",
        json={
            "function_name": "get_notifications",
            "llm_output": "Test LLM output",
            "backend_output": {
                "notifications": [
                    {"title": "Test Title", "description": "Test Description"}
                ]
            },
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" in str(response.json())


def test_get_balance(client):
    response = client.post(
        "/chat/v3/build_ui",
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
    assert "'ui'" in str(response.json())


def test_get_weather(client):
    response = client.post(
        "/chat/v3/build_ui",
        json={
            "function_name": "get_weather",
            "llm_output": "Test LLM output",
            "backend_output": {
                "city": "New York",
                "condition": "Sunny",
                "temperature": 25,
                "feels_like": 27,
                "humidity": 60,
                "sunrise": "06:30",
                "wind_speed": 10,
                "sunset": "20:15",
            },
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" in str(response.json())


def test_get_news(client):
    response = client.post(
        "/chat/v3/build_ui",
        json={
            "function_name": "get_news",
            "llm_output": "Test LLM output",
            "backend_output": {
                "news_items": [
                    {
                        "title": "Test Title",
                        "source": "Test Source",
                        "time": "Test Time",
                        "image_url": "Test Image URL",
                        "url": "Test URL",
                    },
                    {
                        "title": "Test Title",
                        "source": "Test Source",
                        "time": "Test Time",
                        "image_url": "Test Image URL",
                        "url": "Test URL",
                    },
                    {
                        "title": "Test Title",
                        "source": "Test Source",
                        "time": "Test Time",
                        "image_url": "Test Image URL",
                        "url": "Test URL",
                    },
                ],
                "header_text": "Test Header Text",
            },
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" in str(response.json())


def test_get_products(client):
    response = client.post(
        "/chat/v3/build_ui",
        json={
            "function_name": "get_products",
            "llm_output": "Test LLM output",
            "backend_output": {
                "products": [
                    {
                        "id": "1",
                        "title": "Test Title",
                        "price": "1000",
                        "img": "Test Image URL",
                        "desc": "Test Description",
                        "rating": "Test Rating",
                        "installment": "Test Installment",
                        "primary_button": "Test Primary Button",
                    },
                    {
                        "id": "2",
                        "title": "Test Title",
                        "price": "1000",
                        "img": "Test Image URL",
                        "desc": "Test Description",
                        "rating": "Test Rating",
                        "installment": "Test Installment",
                        "primary_button": "Test Primary Button",
                    },
                    {
                        "id": "3",
                        "title": "Test Title",
                        "price": "1000",
                        "img": "Test Image URL",
                        "desc": "Test Description",
                        "rating": "Test Rating",
                        "installment": "Test Installment",
                        "primary_button": "Test Primary Button",
                    },
                ],
                "title": "Test Title",
            },
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" in str(response.json())


def test_chatbot_answer(client):
    response = client.post(
        "/chat/v3/build_ui",
        json={
            "function_name": "chatbot_answer",
            "llm_output": "Test LLM output",
            "backend_output": {},
        },
    )
    print(response.json())
    assert response.status_code == 200
    assert "widgets" in response.json()
    assert "'ui'" in str(response.json())


# def test_get_receiver_id_by_reciver_phone_number(self):
#     response = self.client.post(
#         "/chat/v3/build_ui",
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
#     assert "'ui'" in str(response.json())


# def test_invalid_function_name(self):
#     response = self.client.post(
#         "/chat/v3/build_ui",
