import pydivkit as dv
import json


def contact_widget(name, avatar_url, subtitle):
    return dv.DivContainer(
        orientation="horizontal",
        items=[
            dv.DivImage(
                image_url=avatar_url,
                width=dv.DivFixedSize(value=40),
                height=dv.DivFixedSize(value=40),
                scale=dv.DivImageScale.FILL,
                margins=dv.DivEdgeInsets(right=12),
                border=dv.DivBorder(corner_radius=20),
            ),
            dv.DivContainer(
                orientation="vertical",
                items=[
                    dv.DivText(
                        text=name,
                        font_size=14,
                        font_weight="medium",
                        text_color="#111827",
                    ),
                    dv.DivText(text=subtitle, font_size=12, text_color="#6B7280"),
                ],
            ),
        ],
        paddings=dv.DivEdgeInsets(top=12, bottom=12, right=12, left=12),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")),
        width=dv.DivMatchParentSize(),
    )


if __name__ == "__main__":
    name = "Aslon Khamidov"
    avatar_url = "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRo8jLMi-7Tv_6BwGJ6n-m10tDsTJwbEIDC4cfnPYjeMpN-RnB400RbNJxoDAIO93K7mb1qbVBYhh1KPSOoCd58_wMsQ3pV86hnWJK-xg"
    subtitle = "Hello world"
    # Создание и сохранение JSON
    root = contact_widget(name, avatar_url, subtitle)

    with open("jsons/contact.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
