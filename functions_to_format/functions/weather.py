import pydivkit as dv
import json
from pydantic import BaseModel
from typing import Optional
from .general import (
    Widget,
    TextWidget,
    build_text_widget,
    add_ui_to_widget,
    ButtonsWidget,
    build_buttons_row,
    WidgetInput,
)
from tool_call_models.weather import WeatherResponse
from models.build import BuildOutput


def get_weather_info(llm_output: str, backend_output: dict, version: str = "v3"):
    weather_data = WeatherResponse(**backend_output)
    widget = Widget(
        name="weather_widget",
        type="weather_widget",
        order=2,
        layout="vertical",
        fields=[
            "city",
            "condition",
            "temperature",
            "feels_like",
            "humidity",
            "sunrise",
            "wind_speed",
            "sunset",
        ],
    )
    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget, args={"text": llm_output}
            ),
            build_weather_widget: WidgetInput(
                widget=widget,
                args={"weather_data": weather_data},
            ),
        },
        version,
    )
    return BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


def weather_widget(data: WeatherResponse):
    # Main weather card container
    main_container = dv.DivContainer(
        orientation="vertical",
        width=dv.DivFixedSize(value=320),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(corner_radius=16, stroke=dv.DivStroke(color="#E5E7EB")),
        paddings=dv.DivEdgeInsets(top=20, bottom=20, left=20, right=20),
        margins=dv.DivEdgeInsets(top=16, left=20, right=20, bottom=16),
        items=[
            # Header with city name and location
            dv.DivContainer(
                orientation="horizontal",
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                items=[
                    dv.DivContainer(
                        orientation="vertical",
                        items=[
                            dv.DivText(
                                text=data.location.name,
                                font_size=24,
                                font_weight="bold",
                                text_color="#1F2937",
                            ),
                            dv.DivText(
                                text=f"{data.location.name}, {data.location.country}",
                                font_size=14,
                                text_color="#6B7280",
                            ),
                        ],
                    ),
                    # Weather icon
                    dv.DivText(
                        text="☀️",
                        font_size=48,
                    )
                    if data.current.condition.icon is None
                    else dv.DivImage(
                        image_url="https:" + data.current.condition.icon,
                        width=dv.DivFixedSize(value=48),
                        height=dv.DivFixedSize(value=48),
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=16),
            ),
            # Main temperature and condition section
            dv.DivContainer(
                orientation="horizontal",
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                items=[
                    dv.DivContainer(
                        orientation="vertical",
                        items=[
                            dv.DivText(
                                text=f"{data.current.temp_c}°C",
                                font_size=48,
                                font_weight="bold",
                                text_color="#1F2937",
                            ),
                            dv.DivText(
                                text=f"Ощущается как {data.current.feelslike_c}°C",
                                font_size=14,
                                text_color="#6B7280",
                            ),
                            dv.DivText(
                                text=f"Ветер: {data.current.wind_dir} {data.current.wind_mph} миль/ч",
                                font_size=14,
                                text_color="#6B7280",
                            ),
                            dv.DivText(
                                text=f"Влажность: {data.current.humidity}%",
                                font_size=14,
                                text_color="#6B7280",
                            ),
                            dv.DivText(
                                text=data.current.last_updated,
                                font_size=14,
                                text_color="#6B7280",
                            ),
                        ],
                    ),
                    dv.DivContainer(
                        orientation="vertical",
                        alignment_horizontal="center",
                        items=[
                            dv.DivText(
                                text=data.current.condition.text,
                                font_size=18,
                                font_weight="medium",
                                text_color="#1F2937",
                            ),
                        ],
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=24),
            ),
            # Weekly forecast section
            dv.DivContainer(
                orientation="horizontal",
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                items=[
                    # Generate forecast days dynamically
                    *[
                        dv.DivContainer(
                            orientation="vertical",
                            alignment_horizontal="center",
                            items=[
                                dv.DivText(
                                    text=forecast_day.date.split("-")[2]
                                    if len(forecast_day.date.split("-")) > 2
                                    else forecast_day.date[:3],
                                    font_size=12,
                                    text_color="#6B7280",
                                ),
                                dv.DivText(
                                    text="☀️",
                                    font_size=24,
                                )
                                if forecast_day.day.condition.icon is None
                                else dv.DivImage(
                                    image_url="https:"
                                    + forecast_day.day.condition.icon,
                                    width=dv.DivFixedSize(value=24),
                                    height=dv.DivFixedSize(value=24),
                                ),
                                dv.DivText(
                                    text=f"{forecast_day.day.maxtemp_c}°C",
                                    font_size=12,
                                    font_weight="bold",
                                    text_color="#1F2937",
                                ),
                                dv.DivText(
                                    text=f"{forecast_day.day.mintemp_c}°C",
                                    font_size=12,
                                    text_color="#6B7280",
                                ),
                            ],
                            width=dv.DivFixedSize(value=40),
                        )
                        for forecast_day in data.forecast.forecastday[
                            :6
                        ]  # Show up to 6 days
                    ]
                ],
            ),
        ],
    )

    return main_container


def build_weather_widget(weather_data: WeatherResponse):
    # Create weather widget
    widget = weather_widget(weather_data)
    with open("build_weather_widget.json", "w") as f:
        json.dump(dv.make_div(widget), f, indent=2, ensure_ascii=False)

    # Return the widget as a JSON-serializable object
    return dv.make_div(widget)


if __name__ == "__main__":
    # Sample data
    sample_data = WeatherResponse(
        **{
            "location": {
                "name": "Tashkent",
                "region": "Toshkent",
                "country": "Uzbekistan",
                "lat": 41.3167,
                "lon": 69.25,
                "tz_id": "Asia/Tashkent",
                "localtime_epoch": 1753078603,
                "localtime": "2025-07-21 11:16",
            },
            "current": {
                "last_updated_epoch": 1753078500,
                "last_updated": "2025-07-21 11:15",
                "temp_c": 35.4,
                "temp_f": 95.7,
                "is_day": 1,
                "condition": {
                    "text": "Sunny",
                    "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                    "code": 1000,
                },
                "wind_mph": 5.4,
                "wind_kph": 8.6,
                "wind_degree": 275,
                "wind_dir": "W",
                "pressure_mb": 1004.0,
                "pressure_in": 29.65,
                "precip_mm": 0.0,
                "precip_in": 0.0,
                "humidity": 28,
                "cloud": 0,
                "feelslike_c": 33.7,
                "feelslike_f": 92.6,
                "windchill_c": 38.8,
                "windchill_f": 101.8,
                "heatindex_c": 38.2,
                "heatindex_f": 100.7,
                "dewpoint_c": 6.6,
                "dewpoint_f": 43.8,
                "vis_km": 10.0,
                "vis_miles": 6.0,
                "uv": 8.7,
                "gust_mph": 6.2,
                "gust_kph": 9.9,
            },
            "forecast": {
                "forecastday": [
                    {
                        "date": "2025-07-21",
                        "date_epoch": 1753056000,
                        "day": {
                            "maxtemp_c": 43.2,
                            "maxtemp_f": 109.7,
                            "mintemp_c": 27.5,
                            "mintemp_f": 81.5,
                            "avgtemp_c": 35.7,
                            "avgtemp_f": 96.2,
                            "maxwind_mph": 9.6,
                            "maxwind_kph": 15.5,
                            "totalprecip_mm": 0.0,
                            "totalprecip_in": 0.0,
                            "totalsnow_cm": 0.0,
                            "avgvis_km": 10.0,
                            "avgvis_miles": 6.0,
                            "avghumidity": 16,
                            "daily_will_it_rain": 0,
                            "daily_chance_of_rain": 0,
                            "daily_will_it_snow": 0,
                            "daily_chance_of_snow": 0,
                            "condition": {
                                "text": "Sunny",
                                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                                "code": 1000,
                            },
                            "uv": 2.7,
                        },
                        "astro": {
                            "sunrise": "05:08 AM",
                            "sunset": "07:51 PM",
                            "moonrise": "12:58 AM",
                            "moonset": "05:08 PM",
                            "moon_phase": "Waning Crescent",
                            "moon_illumination": 18,
                            "is_moon_up": 0,
                            "is_sun_up": 0,
                        },
                    },
                    {
                        "date": "2025-07-22",
                        "date_epoch": 1753142400,
                        "day": {
                            "maxtemp_c": 44.0,
                            "maxtemp_f": 111.2,
                            "mintemp_c": 27.7,
                            "mintemp_f": 81.9,
                            "avgtemp_c": 35.7,
                            "avgtemp_f": 96.3,
                            "maxwind_mph": 11.2,
                            "maxwind_kph": 18.0,
                            "totalprecip_mm": 0.0,
                            "totalprecip_in": 0.0,
                            "totalsnow_cm": 0.0,
                            "avgvis_km": 10.0,
                            "avgvis_miles": 6.0,
                            "avghumidity": 12,
                            "daily_will_it_rain": 0,
                            "daily_chance_of_rain": 0,
                            "daily_will_it_snow": 0,
                            "daily_chance_of_snow": 0,
                            "condition": {
                                "text": "Sunny",
                                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                                "code": 1000,
                            },
                            "uv": 2.6,
                        },
                        "astro": {
                            "sunrise": "05:09 AM",
                            "sunset": "07:50 PM",
                            "moonrise": "01:50 AM",
                            "moonset": "06:16 PM",
                            "moon_phase": "Waning Crescent",
                            "moon_illumination": 10,
                            "is_moon_up": 1,
                            "is_sun_up": 0,
                        },
                    },
                    {
                        "date": "2025-07-23",
                        "date_epoch": 1753228800,
                        "day": {
                            "maxtemp_c": 43.4,
                            "maxtemp_f": 110.2,
                            "mintemp_c": 28.2,
                            "mintemp_f": 82.7,
                            "avgtemp_c": 35.8,
                            "avgtemp_f": 96.4,
                            "maxwind_mph": 13.6,
                            "maxwind_kph": 22.0,
                            "totalprecip_mm": 0.0,
                            "totalprecip_in": 0.0,
                            "totalsnow_cm": 0.0,
                            "avgvis_km": 10.0,
                            "avgvis_miles": 6.0,
                            "avghumidity": 10,
                            "daily_will_it_rain": 0,
                            "daily_chance_of_rain": 0,
                            "daily_will_it_snow": 0,
                            "daily_chance_of_snow": 0,
                            "condition": {
                                "text": "Sunny",
                                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                                "code": 1000,
                            },
                            "uv": 2.7,
                        },
                        "astro": {
                            "sunrise": "05:10 AM",
                            "sunset": "07:49 PM",
                            "moonrise": "02:53 AM",
                            "moonset": "07:12 PM",
                            "moon_phase": "Waning Crescent",
                            "moon_illumination": 4,
                            "is_moon_up": 1,
                            "is_sun_up": 0,
                        },
                    },
                    {
                        "date": "2025-07-24",
                        "date_epoch": 1753315200,
                        "day": {
                            "maxtemp_c": 41.2,
                            "maxtemp_f": 106.2,
                            "mintemp_c": 23.9,
                            "mintemp_f": 75.0,
                            "avgtemp_c": 33.1,
                            "avgtemp_f": 91.5,
                            "maxwind_mph": 13.9,
                            "maxwind_kph": 22.3,
                            "totalprecip_mm": 0.0,
                            "totalprecip_in": 0.0,
                            "totalsnow_cm": 0.0,
                            "avgvis_km": 10.0,
                            "avgvis_miles": 6.0,
                            "avghumidity": 10,
                            "daily_will_it_rain": 0,
                            "daily_chance_of_rain": 0,
                            "daily_will_it_snow": 0,
                            "daily_chance_of_snow": 0,
                            "condition": {
                                "text": "Sunny",
                                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                                "code": 1000,
                            },
                            "uv": 2.6,
                        },
                        "astro": {
                            "sunrise": "05:11 AM",
                            "sunset": "07:48 PM",
                            "moonrise": "04:05 AM",
                            "moonset": "07:55 PM",
                            "moon_phase": "New Moon",
                            "moon_illumination": 1,
                            "is_moon_up": 1,
                            "is_sun_up": 0,
                        },
                    },
                    {
                        "date": "2025-07-25",
                        "date_epoch": 1753401600,
                        "day": {
                            "maxtemp_c": 41.3,
                            "maxtemp_f": 106.4,
                            "mintemp_c": 24.7,
                            "mintemp_f": 76.4,
                            "avgtemp_c": 33.5,
                            "avgtemp_f": 92.4,
                            "maxwind_mph": 13.2,
                            "maxwind_kph": 21.2,
                            "totalprecip_mm": 0.0,
                            "totalprecip_in": 0.0,
                            "totalsnow_cm": 0.0,
                            "avgvis_km": 10.0,
                            "avgvis_miles": 6.0,
                            "avghumidity": 10,
                            "daily_will_it_rain": 0,
                            "daily_chance_of_rain": 0,
                            "daily_will_it_snow": 0,
                            "daily_chance_of_snow": 0,
                            "condition": {
                                "text": "Sunny",
                                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                                "code": 1000,
                            },
                            "uv": 3.5,
                        },
                        "astro": {
                            "sunrise": "05:12 AM",
                            "sunset": "07:47 PM",
                            "moonrise": "05:20 AM",
                            "moonset": "08:29 PM",
                            "moon_phase": "Waxing Crescent",
                            "moon_illumination": 0,
                            "is_moon_up": 0,
                            "is_sun_up": 0,
                        },
                    },
                    {
                        "date": "2025-07-26",
                        "date_epoch": 1753488000,
                        "day": {
                            "maxtemp_c": 42.1,
                            "maxtemp_f": 107.8,
                            "mintemp_c": 26.9,
                            "mintemp_f": 80.4,
                            "avgtemp_c": 35.0,
                            "avgtemp_f": 95.1,
                            "maxwind_mph": 13.0,
                            "maxwind_kph": 20.9,
                            "totalprecip_mm": 0.0,
                            "totalprecip_in": 0.0,
                            "totalsnow_cm": 0.0,
                            "avgvis_km": 10.0,
                            "avgvis_miles": 6.0,
                            "avghumidity": 12,
                            "daily_will_it_rain": 0,
                            "daily_chance_of_rain": 0,
                            "daily_will_it_snow": 0,
                            "daily_chance_of_snow": 0,
                            "condition": {
                                "text": "Sunny",
                                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                                "code": 1000,
                            },
                            "uv": 9.0,
                        },
                        "astro": {
                            "sunrise": "05:13 AM",
                            "sunset": "07:46 PM",
                            "moonrise": "06:34 AM",
                            "moonset": "08:56 PM",
                            "moon_phase": "Waxing Crescent",
                            "moon_illumination": 2,
                            "is_moon_up": 0,
                            "is_sun_up": 0,
                        },
                    },
                    {
                        "date": "2025-07-27",
                        "date_epoch": 1753574400,
                        "day": {
                            "maxtemp_c": 38.8,
                            "maxtemp_f": 101.9,
                            "mintemp_c": 27.3,
                            "mintemp_f": 81.1,
                            "avgtemp_c": 33.3,
                            "avgtemp_f": 91.9,
                            "maxwind_mph": 13.4,
                            "maxwind_kph": 21.6,
                            "totalprecip_mm": 0.0,
                            "totalprecip_in": 0.0,
                            "totalsnow_cm": 0.0,
                            "avgvis_km": 10.0,
                            "avgvis_miles": 6.0,
                            "avghumidity": 19,
                            "daily_will_it_rain": 0,
                            "daily_chance_of_rain": 0,
                            "daily_will_it_snow": 0,
                            "daily_chance_of_snow": 0,
                            "condition": {
                                "text": "Sunny",
                                "icon": "//cdn.weatherapi.com/weather/64x64/day/113.png",
                                "code": 1000,
                            },
                            "uv": 8.0,
                        },
                        "astro": {
                            "sunrise": "05:14 AM",
                            "sunset": "07:45 PM",
                            "moonrise": "07:44 AM",
                            "moonset": "09:19 PM",
                            "moon_phase": "Waxing Crescent",
                            "moon_illumination": 6,
                            "is_moon_up": 0,
                            "is_sun_up": 0,
                        },
                    },
                ]
            },
        }
    )

    # Создание и сохранение JSON
    root = weather_widget(sample_data)

    with open("jsons/weather.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
