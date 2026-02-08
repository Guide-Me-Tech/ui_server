from smarty_ui.composites import assistant_bubble
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
    return assistant_bubble(text)


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
