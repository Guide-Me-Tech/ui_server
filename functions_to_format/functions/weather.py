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


class WeatherData(BaseModel):
    city: str
    condition: str
    temperature: int
    feels_like: int
    humidity: int
    sunrise: str
    wind_speed: int
    sunset: str


def get_weather(llm_output: str, backend_output: dict, version: str = "v3"):
    weather_data = WeatherData(**backend_output)
    widget = Widget(
        name="weather_widget",
        type="weather_widget",
        order=1,
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

    widgets = add_ui_to_widget(
        {
            build_weather_widget: WidgetInput(
                widget=widget,
                args={"weather_data": weather_data},
            ),
        },
        version,
    )
    return {
        "widgets_count": 1,
        "widgets": [widget.model_dump_json() for widget in widgets],
    }


def weather_widget(data: WeatherData):
    # Верхняя часть с температурой и заголовком
    top_section = dv.DivContainer(
        orientation="vertical",
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        background=[
            dv.DivLinearGradient(
                angle=135,
                colors=["#3B82F6", "#6366F1"],  # from-blue-500 to-indigo-600
            )
        ],
        paddings=dv.DivEdgeInsets(top=16, bottom=16, left=16, right=16),
        items=[
            dv.DivContainer(
                orientation="horizontal",
                items=[
                    dv.DivContainer(
                        orientation="vertical",
                        items=[
                            dv.DivText(
                                text=data.city,
                                font_size=18,
                                font_weight="bold",
                                text_color="#FFFFFF",
                            ),
                            dv.DivText(
                                text=data.condition, font_size=13, text_color="#E0E7FF"
                            ),
                        ],
                        width=dv.DivMatchParentSize(),
                    )
                ],
            ),
            dv.DivContainer(
                orientation="horizontal",
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                items=[
                    dv.DivText(
                        text=f"{data.temperature}°",
                        font_size=48,
                        font_weight="bold",
                        text_color="#FFFFFF",
                    ),
                    dv.DivContainer(
                        orientation="vertical",
                        alignment_horizontal="right",
                        items=[
                            dv.DivText(
                                text=f"Feels like {data.feels_like}°",
                                font_size=13,
                                text_color="#E0E7FF",
                            ),
                            dv.DivText(
                                text=f"Humidity: {data.humidity}%",
                                font_size=13,
                                text_color="#E0E7FF",
                            ),
                        ],
                    ),
                ],
                margins=dv.DivEdgeInsets(top=12),
            ),
        ],
    )

    # Нижняя панель с иконками (Sunrise, Wind, Sunset)
    bottom_section = dv.DivContainer(
        orientation="horizontal",
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        paddings=dv.DivEdgeInsets(top=16, bottom=16, left=16, right=16),
        items=[
            dv.DivContainer(
                orientation="vertical",
                alignment_horizontal="center",
                items=[
                    dv.DivText(text="🌅", font_size=20),
                    dv.DivText(text="Sunrise", font_size=12, text_color="#374151"),
                    dv.DivText(text=data.sunrise, font_size=13, font_weight="bold"),
                ],
                width=dv.DivFixedSize(value=80),
            ),
            dv.DivContainer(
                orientation="vertical",
                alignment_horizontal="center",
                items=[
                    dv.DivText(text="💨", font_size=20),
                    dv.DivText(text="Wind", font_size=12, text_color="#374151"),
                    dv.DivText(
                        text=f"{data.wind_speed} km/h", font_size=13, font_weight="bold"
                    ),
                ],
                width=dv.DivFixedSize(value=80),
            ),
            dv.DivContainer(
                orientation="vertical",
                alignment_horizontal="center",
                items=[
                    dv.DivText(text="🌇", font_size=20),
                    dv.DivText(text="Sunset", font_size=12, text_color="#374151"),
                    dv.DivText(text=data.sunset, font_size=13, font_weight="bold"),
                ],
                width=dv.DivFixedSize(value=80),
            ),
        ],
    )

    # Обёртка
    return dv.DivContainer(
        orientation="vertical",
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivFixedSize(value=320),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(corner_radius=20, stroke=dv.DivStroke(color="#E5E7EB")),
        items=[top_section, bottom_section],
    )


def build_weather_widget(weather_data: WeatherData):
    # Create weather widget
    widget = weather_widget(weather_data)

    # Return the widget as a JSON-serializable object
    return dv.make_div(widget)


if __name__ == "__main__":
    # Sample data
    sample_data = WeatherData(
        city="Tashkent",
        condition="Partly cloudy",
        temperature=32,
        feels_like=28,
        humidity=45,
        sunrise="6:10",
        wind_speed=12,
        sunset="18:45",
    )

    # Создание и сохранение JSON
    root = weather_widget(sample_data)

    with open("jsons/weather.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
