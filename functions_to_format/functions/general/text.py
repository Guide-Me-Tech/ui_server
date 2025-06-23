from models.widget import Widget
import pydivkit as dv
import json


class TextWidget(Widget):
    name: str = "text_widget"
    type: str = "text_widget"
    layout: str = "horizontal"
    fields: list[str] = ["text"]


def text_widget(
    text: str,
):
    return dv.DivContainer(
        orientation="vertical",
        background=[dv.DivSolidBackground(color="#F8FAFF")],  # light bluish-white
        border=dv.DivBorder(corner_radius=16),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=12, bottom=12),
        items=[
            dv.DivText(
                text=text,
                font_family="Manrope",
                font_size=14,
                font_weight=dv.DivFontWeight.LIGHT,
                text_color="#111133",  # dark navy color
                line_height=20,
                letter_spacing=0,
            )
        ],
        margins=dv.DivEdgeInsets(top=16, left=20),
        width=dv.DivFixedSize(value=280),
        # item_spacing=10,  # gap between items
    )


def build_text_widget(text: str):
    # raise NotImplementedError
    if len(text) == 0:
        return None
    div = dv.make_div(text_widget(text))
    with open("text_widget.json", "w", encoding="utf-8") as f:
        json.dump(div, f, indent=2, ensure_ascii=False)
    return div


if __name__ == "__main__":
    print(build_text_widget("test"))
