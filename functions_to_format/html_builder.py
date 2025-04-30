from jinja2 import Environment, FileSystemLoader
import sys
import os
import logfire

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from conf import logger

env = Environment(loader=FileSystemLoader("templates"))


def weather_widget(*args, **kwargs):

    logger.info("Weather widget")
    logger.info("Args: ", args=args)
    logger.info("Kwargs:", kwarg=kwargs)
    template = env.get_template("weather.html")
    html = template.render(**kwargs)
    return html


if __name__ == "__main__":
    with logfire.span("Buildiing weather widget"):
        logger.info(
            weather_widget(
                **{
                    "wind_speed": "12",
                    "sunset_time": 123,
                    "sunrise_time": "123",
                    "temperature": "132",
                }
            )
        )
