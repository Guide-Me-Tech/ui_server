from .functions import chatbot_answer, unauthorized_response, build_contacts_list
from .balance import get_balance, build_balance_ui, get_home_balances
from .payment import (
    get_receiver_id_by_receiver_phone_number,
    get_categories,
    get_fields_of_supplier,
    get_suppliers_by_category,
    get_number_by_receiver_name,
    send_money_to_someone_via_card,
)
from .contact import build_contact_widget, get_contact
from .news import build_news_widget, get_news
from .notification import build_notifications_widget, get_notifications
from .products import build_products_list_widget, get_products, search_products
from .weather import build_weather_widget, get_weather_info
from .buttons import build_buttons_row
from .start_page import start_page_widget


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
    "get_weather_info": get_weather_info,
    "get_news": get_news,
    "get_products": get_products,
    "search_products": search_products,
    "get_notifications": get_notifications,
    "get_contact": get_contact,
    "chatbot_answer": chatbot_answer,
    "unauthorized_response": unauthorized_response,
    "get_number_by_receiver_name": get_number_by_receiver_name,
    "get_receiver_id_by_reciver_phone_number": get_receiver_id_by_receiver_phone_number,
    "get_receiver_id_by_receiver_phone_number": get_receiver_id_by_receiver_phone_number,
    "get_categories": get_categories,
    "get_fields_of_supplier": get_fields_of_supplier,
    "get_suppliers_by_category": get_suppliers_by_category,
    "start_page_widget": start_page_widget,
    "send_money_to_someone_via_card": send_money_to_someone_via_card,
    "get_home_balances": get_home_balances,
    "build_contacts_list": build_contacts_list,
}
