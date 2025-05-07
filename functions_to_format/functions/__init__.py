from .functions import (
    chatbot_answer,
    unauthorized_response,
)
from .balance import get_balance, build_balance_ui
from .payment import (
    get_receiver_id_by_reciver_phone_number,
    get_categories,
    get_fields_of_supplier,
    get_suppliers_by_category,
)
from .contact import build_contact_widget, get_contact
from .news import build_news_widget, get_news
from .notification import build_notifications_widget, get_notifications
from .products import build_products_list_widget, get_products
from .weather import build_weather_widget, get_weather
from .buttons import build_buttons_row


sdui_functions_map = {
    "notifications": build_notifications_widget,
    "get_balance": build_balance_ui,
    "contact": build_contact_widget,
    "news": build_news_widget,
    "products": build_products_list_widget,
    "weather": build_weather_widget,
    "get_receiver_id_by_reciver_phone_number": None,
    "get_categories": None,
    "get_fields_of_supplier": None,
    "get_suppliers_by_category": None,
    "chatbot_answer": None,
    "text_widget": None,
    "buttons_widget": build_buttons_row,
}
functions_mapper = {
    "get_balance": get_balance,
    "get_weather": get_weather,
    "get_news": get_news,
    "get_products": get_products,
    "get_notifications": get_notifications,
    "get_contact": get_contact,
    "chatbot_answer": chatbot_answer,
    "unauthorized_response": unauthorized_response,
    "get_receiver_id_by_reciver_phone_number": get_receiver_id_by_reciver_phone_number,
    "get_categories": get_categories,
    "get_fields_of_supplier": get_fields_of_supplier,
    "get_suppliers_by_category": get_suppliers_by_category,
}
