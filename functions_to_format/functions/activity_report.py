import pydivkit as dv
import json
from pydantic import BaseModel
from typing import Any, Dict, List
from pydivkit.core import Expr
import structlog

from functions_to_format.functions.balance import (
    build_balance_ui,
    build_home_balances_ui,
)
from .general import Widget, add_ui_to_widget, WidgetInput
from .general.utils import save_builder_output
from models.build import BuildOutput
from functions_to_format.functions.general.const_values import LanguageOptions
from models.context import Context, LoggerContext

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    text_1,
    text_2,
    caption_1,
    caption_2,
    default_theme,
)

logger = structlog.get_logger(__name__)


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
    """Trigger row: message + chevron (like ReasoningTrigger). Tapping toggles state.

    Uses smarty_ui HStack for horizontal layout.
    """
    set_state_url = f"div-action://set_state?state_id=0/{state_id}/{target_state}"

    # Message container with flex weight
    message_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(weight=1),
        items=[_message_glow_text(message)],
    )

    # Chevron text
    chevron_text = dv.DivText(
        text=chevron,
        font_size=16,
        text_color=CHEVRON_COLOR,
    )

    # Use HStack for horizontal layout
    trigger = HStack(
        [message_container, chevron_text],
        gap=GAP_MESSAGE_CHEVRON,
        align_v="center",
        padding_left=TRIGGER_PADDING_H,
        padding_right=TRIGGER_PADDING_H,
        padding_top=TRIGGER_PADDING_V,
        padding_bottom=TRIGGER_PADDING_V,
        background=MESSAGE_BLOCK_BG,
        corner_radius=TRIGGER_RADIUS,
    )

    # Add border stroke and action manually (not supported by HStack helper)
    trigger.border = dv.DivBorder(
        corner_radius=TRIGGER_RADIUS,
        stroke=dv.DivStroke(color="#4B5563", width=1),
    )
    trigger.action = dv.DivAction(log_id=log_id, url=set_state_url)

    return trigger


def _build_activity_message_holder(
    message: str,
    title: str,
    detail_json: str,
    log_id: str,
    action_url: str = "div-action://activity-report",
):
    """Reasoning-like collapsible: trigger row (message + chevron) + expandable content (title + detail).

    Uses smarty_ui VStack for vertical layouts.
    """
    state_id = f"activity_{log_id}"

    # Collapsed: only trigger row with ▼ (expand)
    collapsed_trigger = _trigger_row(
        message=message,
        chevron="▼",
        state_id=state_id,
        target_state="expanded",
        log_id=log_id,
    )

    # Content inner using VStack
    title_text = caption_1(title, color=CONTENT_TITLE_COLOR)
    detail_text = caption_2(detail_json, color=CONTENT_DETAIL_COLOR)

    content_inner = VStack(
        [title_text, detail_text],
        gap=8,
    )

    # Content block with styling
    content_block = VStack(
        [content_inner],
        padding=CONTENT_PADDING,
        background=CONTENT_BLOCK_BG,
        corner_radius=CONTENT_RADIUS,
    )
    content_block.margins = dv.DivEdgeInsets(top=SPACING_ABOVE_CONTENT)
    content_block.border = dv.DivBorder(
        corner_radius=CONTENT_RADIUS,
        stroke=dv.DivStroke(color=CONTENT_BLOCK_BORDER, width=1),
    )
    content_block.transition_in = dv.DivFadeTransition(duration=200, alpha=0.5)

    # Expanded trigger
    expanded_trigger = _trigger_row(
        message=message,
        chevron="▲",
        state_id=state_id,
        target_state="collapsed",
        log_id=log_id,
    )

    # Expanded div using VStack
    expanded_div = VStack([expanded_trigger, content_block])

    state = dv.DivState(
        id=state_id,
        default_state_id="expanded",
        states=[
            dv.DivStateState(state_id="collapsed", div=collapsed_trigger),
            dv.DivStateState(state_id="expanded", div=expanded_div),
        ],
    )

    widgets = [state]

    # Wrapper using VStack
    wrapper = VStack(
        widgets,
        padding_left=12,
        padding_right=12,
        padding_top=8,
        padding_bottom=8,
    )

    return dv.make_div(wrapper)


def build_function_call_activity_widget(
    message: str,
    function_name: str,
    arguments: Dict[str, Any],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """Builder for function_call activity: shows message and call details (function_name, arguments)."""
    logger.debug(
        "building_function_call_activity_widget",
        function_name=function_name,
        message=message,
    )
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
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """Builder for function_response activity: shows message and response (function_name, response)."""
    logger.debug(
        "building_function_response_activity_widget",
        function_name=function_name,
        message=message,
    )
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
    """Build activity indicator widget using smarty_ui components."""
    logger.debug("building_activity_indicator_widget", message=message)
    # Use text_1 for the message text
    message_text = text_1(message, color="#F1F5F9")

    # Use VStack for vertical layout
    container = VStack([message_text])
    container.id = "activity_report"
    container.action = dv.DivAction(
        log_id="activity_report",
        url="div-action://activity-report",
        payload={
            "message": message,
            "link": "http://10.212.134.3:8003/new_messages?idx=12341234",
        },
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
    ctx_logger = context.logger_context.logger

    ctx_logger.info("activity_indicator_started", llm_output=llm_output)

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

    ctx_logger.info("activity_indicator_completed", widgets_count=len(widgets))
    save_builder_output(context, output)
    return output
