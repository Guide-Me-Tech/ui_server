from models.widget import Widget
import pydivkit as dv


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
        border=dv.DivBorder(corner_radius=20),  # smooth rounded bubble
        paddings=dv.DivEdgeInsets(left=16, right=16, top=12, bottom=12),
        items=[
            dv.DivText(
                text=text,
                font_size=18,
                font_weight="medium",
                text_color="#111133",  # dark navy color
                line_height=22,
            )
        ],
        margins=dv.DivEdgeInsets(bottom=8),
        width=dv.DivWrapContentSize(),
    )


def build_text_widget(text: str):
    # raise NotImplementedError
    if len(text) == 0:
        return None
    return dv.make_div(text_widget(text))


if __name__ == "__main__":
    print(build_text_widget("test"))
