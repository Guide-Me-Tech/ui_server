import pydivkit as dv
import json


def weather_widget():
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
                                text="Tashkent",
                                font_size=18,
                                font_weight="bold",
                                text_color="#FFFFFF",
                            ),
                            dv.DivText(
                                text="Partly cloudy", font_size=13, text_color="#E0E7FF"
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
                        text="132°",
                        font_size=48,
                        font_weight="bold",
                        text_color="#FFFFFF",
                    ),
                    dv.DivContainer(
                        orientation="vertical",
                        alignment_horizontal="right",
                        items=[
                            dv.DivText(
                                text="Feels like 128°",
                                font_size=13,
                                text_color="#E0E7FF",
                            ),
                            dv.DivText(
                                text="Humidity: 45%", font_size=13, text_color="#E0E7FF"
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
                    dv.DivText(text="6:10", font_size=13, font_weight="bold"),
                ],
                width=dv.DivFixedSize(value=80),
            ),
            dv.DivContainer(
                orientation="vertical",
                alignment_horizontal="center",
                items=[
                    dv.DivText(text="💨", font_size=20),
                    dv.DivText(text="Wind", font_size=12, text_color="#374151"),
                    dv.DivText(text="12 km/h", font_size=13, font_weight="bold"),
                ],
                width=dv.DivFixedSize(value=80),
            ),
            dv.DivContainer(
                orientation="vertical",
                alignment_horizontal="center",
                items=[
                    dv.DivText(text="🌇", font_size=20),
                    dv.DivText(text="Sunset", font_size=12, text_color="#374151"),
                    dv.DivText(text="18:45", font_size=13, font_weight="bold"),
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


if __name__ == "__main__":
    # Создание и сохранение JSON
    root = weather_widget()

    with open("jsons/weather.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
