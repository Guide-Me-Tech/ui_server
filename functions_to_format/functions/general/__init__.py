from typing import Dict, Callable, Any
from .text import build_text_widget, TextWidget
from .buttons import build_buttons_row, ButtonsWidget
from .widget import Widget
from pydantic import BaseModel


class WidgetInput(BaseModel):
    widget: Widget
    args: Dict[str, Any]


def add_ui_to_widget(
    widgets: Dict[Callable, WidgetInput],
    version,
):
    if version == "v3":
        for sdui_function, widget_input in widgets.items():
            widget_args = widget_input.args
            widget_input.widget.build_ui(sdui_function, **widget_args)
    return list(widgets.values())
