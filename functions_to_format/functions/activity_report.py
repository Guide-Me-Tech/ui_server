import pydivkit as dv
import json
from pydantic import BaseModel
from typing import Any, Dict, List
from pydivkit.core import Expr
from .general import Widget, add_ui_to_widget, WidgetInput
from .general.utils import save_builder_output
from models.build import BuildOutput
from functions_to_format.functions.general.const_values import LanguageOptions
from conf import logger
from models.context import Context, LoggerContext
import structlog


# Backend output schemas for activity reports
class FunctionCallBackendOutput(BaseModel):
    """Backend output for function_call activity report."""

    function_name: str
    arguments: Dict[str, Any]


class FunctionResponseBackendOutput(BaseModel):
    """Backend output for function_response activity report."""

    function_name: str
    response: Dict[str, Any]


class ActivityIndicatorWidget(BaseModel):
    message: str


# Reasoning-like design: gray trigger block, muted content
MESSAGE_BLOCK_BG = "#374151"
MESSAGE_TEXT_COLOR = "#F8FAFC"
CONTENT_TITLE_COLOR = "#94A3B8"
CONTENT_DETAIL_COLOR = "#64748B"
CHEVRON_COLOR = "#94A3B8"
# Content block: subtle card so detail feels grouped
CONTENT_BLOCK_BG = "#1E293B"
CONTENT_BLOCK_BORDER = "#334155"
CONTENT_PADDING = 14
TRIGGER_PADDING_V = 12
TRIGGER_PADDING_H = 16
TRIGGER_RADIUS = 10
CONTENT_RADIUS = 8
SPACING_ABOVE_CONTENT = 14
GAP_MESSAGE_CHEVRON = 12


def _message_glow_text(message: str) -> dv.DivText:
    """Message text with glow animation: soft shadow + fade-in transition."""
    shadow_offset = dv.DivPoint(
        x=dv.DivDimension(value=0),
        y=dv.DivDimension(value=0),
    )
    text_shadow = dv.DivShadow(
        offset=shadow_offset,
        color="#7DD3FC",
        blur=10,
        alpha=0.7,
    )
    transition_in = dv.DivFadeTransition(
        duration=600,
        alpha=0.2,
        interpolator=dv.DivAnimationInterpolator.EASE_OUT,
    )
    return dv.DivText(
        text=message,
        font_size=14,
        text_color=MESSAGE_TEXT_COLOR,
        text_shadow=text_shadow,
        transition_in=transition_in,
    )


def _trigger_row(
    message: str,
    chevron: str,
    state_id: str,
    target_state: str,
    log_id: str,
) -> dv.DivContainer:
    """Trigger row: message + chevron (like ReasoningTrigger). Tapping toggles state."""
    set_state_url = f"div-action://set_state?state_id=0/{state_id}/{target_state}"
    return dv.DivContainer(
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        background=[dv.DivSolidBackground(color=MESSAGE_BLOCK_BG)],
        paddings=dv.DivEdgeInsets(
            left=TRIGGER_PADDING_H,
            right=TRIGGER_PADDING_H,
            top=TRIGGER_PADDING_V,
            bottom=TRIGGER_PADDING_V,
        ),
        border=dv.DivBorder(
            corner_radius=TRIGGER_RADIUS,
            stroke=dv.DivStroke(color="#4B5563", width=1),
        ),
        alignment_vertical=dv.DivAlignmentVertical.CENTER,
        items=[
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.VERTICAL,
                width=dv.DivMatchParentSize(weight=1),
                margins=dv.DivEdgeInsets(right=GAP_MESSAGE_CHEVRON),
                items=[_message_glow_text(message)],
            ),
            dv.DivText(
                text=chevron,
                font_size=16,
                text_color=CHEVRON_COLOR,
            ),
        ],
        action=dv.DivAction(log_id=log_id, url=set_state_url),
    )


def _build_activity_message_holder(
    message: str,
    title: str,
    detail_json: str,
    log_id: str,
    action_url: str = "div-action://activity-report",
):
    """Reasoning-like collapsible: trigger row (message + chevron) + expandable content (title + detail)."""
    state_id = f"activity_{log_id}"

    # Collapsed: only trigger row with ▼ (expand)
    collapsed_trigger = _trigger_row(
        message=message,
        chevron="▼",
        state_id=state_id,
        target_state="expanded",
        log_id=log_id,
    )

    # Expanded: trigger row with ▲ (collapse) + content below in a card
    content_inner = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=[
            dv.DivText(
                text=title,
                font_size=13,
                text_color=CONTENT_TITLE_COLOR,
                font_weight=dv.DivFontWeight.MEDIUM,
                margins=dv.DivEdgeInsets(bottom=8),
            ),
            dv.DivText(
                text=detail_json,
                font_size=11,
                text_color=CONTENT_DETAIL_COLOR,
                line_height=18,
            ),
        ],
    )
    content_block = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        margins=dv.DivEdgeInsets(top=SPACING_ABOVE_CONTENT),
        paddings=dv.DivEdgeInsets(
            left=CONTENT_PADDING,
            right=CONTENT_PADDING,
            top=CONTENT_PADDING,
            bottom=CONTENT_PADDING,
        ),
        background=[dv.DivSolidBackground(color=CONTENT_BLOCK_BG)],
        border=dv.DivBorder(
            corner_radius=CONTENT_RADIUS,
            stroke=dv.DivStroke(color=CONTENT_BLOCK_BORDER, width=1),
        ),
        transition_in=dv.DivFadeTransition(duration=200, alpha=0.5),
        items=[content_inner],
    )
    expanded_trigger = _trigger_row(
        message=message,
        chevron="▲",
        state_id=state_id,
        target_state="collapsed",
        log_id=log_id,
    )
    expanded_div = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=[
            expanded_trigger,
            content_block,
        ],
    )

    state = dv.DivState(
        id=state_id,
        default_state_id="expanded",
        states=[
            dv.DivStateState(state_id="collapsed", div=collapsed_trigger),
            dv.DivStateState(state_id="expanded", div=expanded_div),
        ],
    )
    wrapper = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        margins=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
        items=[state],
    )
    return dv.make_div(wrapper)


def build_function_call_activity_widget(
    message: str,
    function_name: str,
    arguments: Dict[str, Any],
):
    """Builder for function_call activity: shows message and call details (function_name, arguments)."""
    title = f"Calling: {function_name}"
    detail_json = json.dumps(arguments, ensure_ascii=False, default=str)[:500]
    if len(detail_json) >= 500:
        detail_json += "..."
    return _build_activity_message_holder(
        message=message,
        title=title,
        detail_json=detail_json,
        log_id="function_call_activity_report",
        action_url="div-action://function-call-activity-report",
    )


def build_function_response_activity_widget(
    message: str,
    function_name: str,
    response: Dict[str, Any],
):
    """Builder for function_response activity: shows message and response (function_name, response)."""
    title = f"Response from: {function_name}"
    detail_json = json.dumps(response, ensure_ascii=False, default=str)[:500]
    if len(detail_json) >= 500:
        detail_json += "..."
    return _build_activity_message_holder(
        message=message,
        title=title,
        detail_json=detail_json,
        log_id="function_response_activity_report",
        action_url="div-action://function-response-activity-report",
    )


def build_activity_indicator_widget(message: str) -> ActivityIndicatorWidget:
    container = dv.DivContainer(
        id="activity_report",
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=[
            dv.DivText(text=message, font_size=14, text_color="#F1F5F9"),
        ],
        action=dv.DivAction(
            log_id="activity_report",
            url="div-action://activity-report",
            payload={
                "message": message,
                "link": "http://10.212.134.3:8003/new_messages?idx=12341234",
            },
        ),
    )

    return dv.make_div(container)


def activity_indicator(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    inp = {}

    activity_indicator_widget = Widget(
        name="activity_indicator_widget",
        type="activity_indicator_widget",
        order=1,
        layout="vertical",
        fields=["activity_indicator"],
    )
    inp[build_activity_indicator_widget] = WidgetInput(
        widget=activity_indicator_widget,
        args={"message": llm_output},
    )
    widgets = add_ui_to_widget(
        widget_inputs=inp,
        version=version,
    )
    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )

    save_builder_output(context, output)
    return output
