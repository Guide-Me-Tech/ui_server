import unittest
from functions_to_format.functions.notification import get_notifications
from functions_to_format.functions.balance import get_balance
from functions_to_format.functions.payment import (
    get_receiver_id_by_reciver_phone_number,
    get_categories,
    get_fields_of_supplier,
    get_suppliers_by_category,
)
from functions_to_format.functions.contact import get_contact
from functions_to_format.functions.news import get_news
from functions_to_format.functions.products import build_products_list_widget
from functions_to_format.functions.weather import build_weather_widget
from functions_to_format.functions.buttons import build_buttons_row
import pydivkit as dv


class TestFunctionsV3(unittest.TestCase):
    def test_get_notifications(self):
        llm_output = "Test LLM output"
        backend_output = {
            "notifications": [
                {"title": "Test Title", "description": "Test Description"}
            ]
        }
        result = get_notifications(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 1)
        self.assertIn("widgets", result)

    def test_get_balance(self):
        llm_output = "Test LLM output"
        backend_output = [
            {
                "pan": "1234",
                "processingSystem": "VISA",
                "balance": 1000,
                "cardDetails": {"cardName": "Test Card", "cardColor": "#FFFFFF"},
            }
        ]
        result = get_balance(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 2)
        self.assertIn("widgets", result)

    def test_get_receiver_id_by_reciver_phone_number(self):
        llm_output = "Test LLM output"
        backend_output = [{"mask": "1234", "name": "Test Name", "processing": "VISA"}]
        result = get_receiver_id_by_reciver_phone_number(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 3)
        self.assertIn("widgets", result)

    def test_get_categories(self):
        llm_output = "Test LLM output"
        backend_output = [
            {"id": 1, "name": "Test Category", "s3Url": "http://example.com/image.png"}
        ]
        result = get_categories(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 3)
        self.assertIn("widgets", result)

    def test_get_fields_of_supplier(self):
        llm_output = "Test LLM output"
        backend_output = {
            "fieldList": [
                {
                    "identName": "amount",
                    "name": "Amount",
                    "order": 1,
                    "type": "MONEY",
                    "pattern": None,
                    "minValue": 100,
                    "maxValue": 1000,
                    "fieldSize": 10,
                    "isMain": True,
                    "valueList": [],
                }
            ]
        }
        result = get_fields_of_supplier(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 3)
        self.assertIn("widgets", result)

    def test_get_suppliers_by_category(self):
        llm_output = "Test LLM output"
        backend_output = [
            {"id": 1, "name": "Test Supplier", "s3Url": "http://example.com/image.png"}
        ]
        result = get_suppliers_by_category(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 3)
        self.assertIn("widgets", result)

    def test_get_contact(self):
        llm_output = "Test LLM output"
        backend_output = {
            "name": "Test Name",
            "avatar_url": "http://example.com/avatar.png",
            "subtitle": "Test Subtitle",
        }
        result = get_contact(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 1)
        self.assertIn("widgets", result)

    def test_get_news(self):
        llm_output = "Test LLM output"
        backend_output = {
            "news_items": [
                {
                    "title": "Test News",
                    "source": "Test Source",
                    "time": "1h",
                    "image_url": "http://example.com/image.png",
                    "url": "http://example.com",
                }
            ],
            "header_text": "Test Header",
        }
        result = get_news(llm_output, backend_output)
        self.assertEqual(result["widgets_count"], 1)
        self.assertIn("widgets", result)

    def test_build_products_list_widget(self):
        llm_output = "Test LLM output"
        backend_output = {
            "products": [
                {
                    "id": "1",
                    "title": "Test Product",
                    "price": "1000",
                    "img": "http://example.com/image.png",
                    "desc": "Test Description",
                    "rating": "5 stars",
                    "installment": "100 per month",
                    "primary_button": "Buy Now",
                }
            ]
        }
        result = build_products_list_widget(backend_output, llm_output)
        self.assertIn("widgets", result)

    def test_build_weather_widget(self):
        llm_output = "Test LLM output"
        backend_output = {
            "location": "Test Location",
            "temperature": "25°C",
            "condition": "Sunny",
            "forecast": [
                {"day": "Monday", "high": "30°C", "low": "20°C", "condition": "Sunny"}
            ],
        }
        result = build_weather_widget(backend_output, llm_output)
        self.assertIn("widgets", result)

    def test_build_buttons_row(self):
        button_texts = ["Submit", "Cancel"]
        result = build_buttons_row(button_texts)
        self.assertIsInstance(result, dv.DivContainer)


if __name__ == "__main__":
    unittest.main()
