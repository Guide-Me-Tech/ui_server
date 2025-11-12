from models.widget import Widget
import pydivkit as dv
import json
from .const_values import WidgetMargins


class TextWidget(Widget):
    name: str = "text_widget"
    type: str = "text_widget"
    layout: str = "horizontal"
    fields: list[str] = ["text"]


def text_widget(
    text: str,
):
    text = text.replace("*", "")
    return dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[dv.DivSolidBackground(color="#F8FAFF")],  # light bluish-white
        border=dv.DivBorder(corner_radius=16),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
        items=[
            dv.DivText(
                text=text + "\n",
                font_family="Manrope",
                font_size=14,
                font_weight=dv.DivFontWeight.LIGHT,
                text_color="#111133",  # dark navy color
                line_height=22,
                letter_spacing=0,
                # max_lines=0,  # Allow unlimited lines
                text_alignment_horizontal=dv.DivAlignmentHorizontal.LEFT,
                text_alignment_vertical=dv.DivAlignmentVertical.TOP,
            )
        ],
        margins=dv.DivEdgeInsets(
            top=WidgetMargins.TOP.value,
            left=WidgetMargins.LEFT.value,
            right=WidgetMargins.RIGHT.value,
            bottom=WidgetMargins.BOTTOM.value,
        ),
        width=dv.DivMatchParentSize(),
        height=dv.DivWrapContentSize(),
        # item_spacing=10,  # gap between items
    )


def build_text_widget(text: str):
    # raise NotImplementedError
    if len(text) == 0:
        return None
    div = dv.make_div(text_widget(text))
    with open("logs/json/text_widget.json", "w", encoding="utf-8") as f:
        json.dump(div, f, indent=2, ensure_ascii=False)
    return div


if __name__ == "__main__":
    print(build_text_widget("test"))
