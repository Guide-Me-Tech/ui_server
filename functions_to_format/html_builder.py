from jinja2 import Environment, FileSystemLoader
import sys
import os
import logfire

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conf import logger

env = Environment(loader=FileSystemLoader("templates"))


def products(*args, **kwargs):
    logger.info("Products widget")
    return env.get_template("products.html").render(**kwargs)


def notifications(*args, **kwargs):
    logger.info("Notifications widget")
    return env.get_template("notifications.html").render(**kwargs)


def balance(*args, **kwargs):
    logger.info("Balance widget")
    logger.info("Kwargs:", kwarg=kwargs)
    template = env.get_template("balance.html")
    return template.render(**kwargs)


def weather_widget(*args, **kwargs):

    logger.info("Weather widget")
    # logger.info("Args: ", args=args)
    # logger.info("Kwargs:", kwarg=kwargs)
    template = env.get_template("weather.html")
    html = template.render(**kwargs)
    return html


if __name__ == "__main__":
    with logfire.span("Buildiing weather widget"):
        with open("temp/weather.html", "w") as f:
            f.write(
                weather_widget(
                    **{
                        "wind_speed": "12",
                        "sunset_time": 123,
                        "sunrise_time": "123",
                        "temperature": "132",
                    }
                )
            )
        with open("temp/balance.html", "w") as f:
            f.write(
                balance(
                    **{
                        "cards": [
                            {
                                "balance": "100000",
                                "image_url": "https://humocard.uz/bitrix/templates/main/img/card2.png",
                                "last_digits": "7777",
                                "type": "humo",
                            },
                            {
                                "image_url": "https://humocard.uz/bitrix/templates/main/img/card2.png",
                                "balance": "150000",
                                "last_digits": "8888",
                                "type": "visa",
                            },
                            {
                                "image_url": "https://humocard.uz/bitrix/templates/main/img/card2.png",
                                "balance": "200000",
                                "last_digits": "9999",
                                "type": "mastercard",
                            },
                            {
                                "image_url": "https://humocard.uz/bitrix/templates/main/img/card2.png",
                                "balance": "250000",
                                "last_digits": "1111",
                                "type": "unionpay",
                            },
                        ],
                        "actions": ["Ok", "Not bad"],
                        "text": "Hahahah Вот баланс ваших карт и счетов, хотите произвести оплату за телефон или перевод?",
                    }
                )
            )

        with open("temp/notifications.html", "w") as f:
            f.write(
                notifications(
                    **{
                        "notifications": [
                            {"title": "hello world", "time": "123123"},
                            {"title": "hello world", "time": "123123"},
                            {"title": "hello world", "time": "123123"},
                            {"title": "hello world", "time": "123123"},
                            {"title": "hello world", "time": "123123"},
                            {"title": "hello world", "time": "123123"},
                            {"title": "hello world", "time": "123123"},
                        ]
                    }
                )
            )
        with open("temp/products.html", "w") as f:
            f.write(
                products(
                    **{
                        "products": [
                            {
                                "name": "Смартфон Nothing Phone",
                                "price": "3 953 000 сум",
                                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6j3LinJbdeph2V4vBVa-IDPHlsStt8LjCQw&s",
                                "description": "Nothing Phone (1) 8/256 ГБ...",
                                "rating": "4.1",
                                "reviews": "12",
                                "installment": {"price": "1 3 400", "period": "12"},
                                "buttons": ["Good"],
                            },
                            {
                                "name": "New Product 1",
                                "price": "1 000 000 сум",
                                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6j3LinJbdeph2V4vBVa-IDPHlsStt8LjCQw&s",
                                "description": "New Product 1 Description...",
                                "rating": "4.5",
                                "reviews": "20",
                                "installment": {"price": "500 000", "period": "6"},
                                "buttons": ["Buy Now"],
                            },
                            {
                                "name": "New Product 2",
                                "price": "2 000 000 сум",
                                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6j3LinJbdeph2V4vBVa-IDPHlsStt8LjCQw&s",
                                "description": "New Product 2 Description...",
                                "rating": "4.8",
                                "reviews": "30",
                                "installment": {"price": "1 000 000", "period": "12"},
                                "buttons": ["Add to Cart"],
                            },
                            {
                                "name": "New Product 3",
                                "price": "3 000 000 сум",
                                "image": "https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcS6j3LinJbdeph2V4vBVa-IDPHlsStt8LjCQw&s",
                                "description": "New Product 3 Description...",
                                "rating": "4.7",
                                "reviews": "25",
                                "installment": {"price": "1 500 000", "period": "18"},
                                "buttons": ["View Details"],
                            },
                            # Add more product dicts if needed
                        ]
                    }
                )
            )
        # with open("temp/balance.html", "w") as f:
        #     f.write(balance(**{}))
        # with open("temp/balance.html", "w") as f:
        #     f.write(balance(**{}))
