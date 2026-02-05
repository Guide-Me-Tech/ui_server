from typing import Dict, Callable, Any, List
from .text import build_text_widget, TextWidget
from .buttons import build_buttons_row, ButtonsWidget
from .action_helpers import (
    create_feedback_variables,
    create_success_actions,
    create_failure_actions,
    create_loading_actions,
    create_success_container,
    create_error_container,
    create_loading_container,
    create_submit_action_with_handlers,
    create_simple_action_with_feedback,
    create_selection_action,
    create_feedback_wrapper,
    get_feedback_text,
    FEEDBACK_TEXTS,
)
from models.widget import Widget
from pydantic import BaseModel
from conf import logger


class WidgetInput(BaseModel):
    widget: Widget
    args: Dict[str, Any]


def add_ui_to_widget(
    widget_inputs: Dict[Callable, WidgetInput],
    version: str,
):
    if version == "v3":
        for sdui_function, widget_input in widget_inputs.items():
            try:
                if (
                    sdui_function.__name__ == "build_text_widget"
                    and len(widget_input.args["text"]) == 0
                ):
                    continue
                widget_args = widget_input.args
                widget_input.widget.build_ui(sdui_function, **widget_args)
            except Exception as e:
                logger.error("Error building widget", error=e)
                logger.exception("Error building widget", error=e)
                continue
    widgets: List[Widget] = []
    for widget_input in widget_inputs.values():
        widgets.append(widget_input.widget)

    return widgets
