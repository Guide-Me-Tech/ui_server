import pydivkit as dv
import json


def notification_widget(title, description):
    return dv.DivContainer(
        orientation="vertical",
        items=[
            dv.DivText(
                text=title, font_size=14, font_weight="bold", text_color="#1E3A8A"
            ),
            dv.DivText(
                text=description,
                font_size=13,
                text_color="#374151",
                margins=dv.DivEdgeInsets(top=4),
            ),
        ],
        paddings=dv.DivEdgeInsets(left=16, right=16, bottom=16, top=16),
        background=[dv.DivSolidBackground(color="#EFF6FF")],
        border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#BFDBFE")),
        width=dv.DivMatchParentSize(),
    )


if __name__ == "__main__":
    title = "Alert"
    description = "Fraudalent transaction"
    root = notification_widget(title, description)

    with open("jsons/notification.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
