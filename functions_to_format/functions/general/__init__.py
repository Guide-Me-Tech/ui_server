from typing import Dict, Callable, Any, List
from .text import build_text_widget, TextWidget
from .buttons import build_buttons_row, ButtonsWidget
from models.widget import Widget
from pydantic import BaseModel


class WidgetInput(BaseModel):
    widget: Widget
    args: Dict[str, Any]


def add_ui_to_widget(
    widget_inputs: Dict[Callable, WidgetInput],
    version: str,
):
    if version == "v3":
        for sdui_function, widget_input in widget_inputs.items():
            if (
                sdui_function.__name__ == "build_text_widget"
                and len(widget_input.args["text"]) == 0
            ):
                continue
            widget_args = widget_input.args
            widget_input.widget.build_ui(sdui_function, **widget_args)
    widgets: List[Widget] = []
    for widget_input in widget_inputs.values():
        widgets.append(widget_input.widget)
    return widgets
