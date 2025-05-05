from .functions import (
    build_notifications_widget,
    build_balance,
    build_contact_widget,
    build_news_widget,
    build_products_list_widget,
    build_weather_widget,
)


sdui_function_map = {
    "notifications": build_notifications_widget,
    "balance": build_balance,
    "contact": build_contact_widget,
    "news": build_news_widget,
    "products": build_products_list_widget,
    "weather": build_weather_widget,
}
