from typing import Any

from pydivkit.core import Expr
from functions_to_format.functions.buttons import build_buttons_row
from .general import (
    Widget,
    WidgetInput,
)
from .base_strategy import FunctionStrategy

from conf import logger
from functions_to_format.functions.general.const_values import (
    LanguageOptions,
    WidgetMargins,
)
import structlog
from models.context import Context
import pydivkit as dv

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    title_2,
    text_1,
    text_2,
    caption_1,
    caption_2,
    primary_button,
    secondary_button,
    default_theme,
)

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


def human_approval_ui(
    human_approval_input: dict[str, Any],
    language: LanguageOptions = LanguageOptions.UZBEK,
    text: str = "",
    api_key: str = "",
):
    """Build a payment success card UI using pydivkit"""
    logger.info(
        "Building human approval UI", language=language, has_api_key=bool(api_key)
    )
    logger.debug("human_approval_input", human_approval_input=human_approval_input)

    texts_map = {
        LanguageOptions.UZBEK: {
            "payment_status": "To'lov miqdori",
            "currency": "so'm",
            "payment_description": "Mahsulot va xizmatlar uchun to'lov",
            "transaction_details": "Tranzaksiya raqami:",
            "date": "O'tkazish vaqti:",
            "sender": "Jo'natuvchi:",
            "receiver": "Qabul qiluvchi:",
        },
        LanguageOptions.RUSSIAN: {
            "payment_status": "Сумма платежа",
            "currency": "cумм.",
            "payment_description": "Платеж за товары и услуги",
            "transaction_details": "Номер транзакции:",
            "date": "Время перевода:",
            "sender": "Отправитель:",
            "receiver": "Получатель:",
        },
        LanguageOptions.ENGLISH: {
            "payment_status": "Payment amount",
            "currency": "USD",
            "payment_description": "Payment for goods and services",
            "transaction_details": "Transaction number:",
            "date": "Transfer time:",
            "sender": "Sender:",
            "receiver": "Receiver:",
        },
    }

    try:
        approve_link = human_approval_input["human_approval_event"]["approve_link"]
        reject_link = human_approval_input["human_approval_event"]["reject_link"]

        logger.info(
            "Generated approval links",
            approve_link_length=len(approve_link),
            reject_link_length=len(reject_link),
        )

        # Build approval info text using smarty_ui
        info_text = text_1(
            "Please approve the action. \n"
            + "user_id: "
            + human_approval_input["human_approval_event"]["user_id"]
            + "\n"
            + "session_id: "
            + human_approval_input["human_approval_event"]["session_id"]
            + "\n"
            + "app_name: "
            + human_approval_input["human_approval_event"]["app_name"]
            + "\n",
            color="#111133",
        )
        info_text.font_weight = dv.DivFontWeight.LIGHT
        info_text.line_height = 22
        info_text.text_alignment_horizontal = dv.DivAlignmentHorizontal.LEFT
        info_text.text_alignment_vertical = dv.DivAlignmentVertical.TOP

        # Text container using VStack
        text_container = VStack(
            [info_text],
            padding=16,
            background="#F8FAFF",
            corner_radius=16,
            width=dv.DivMatchParentSize(),
        )
        text_container.height = dv.DivWrapContentSize()
        text_container.margins = dv.DivEdgeInsets(
            top=WidgetMargins.TOP.value,
            left=WidgetMargins.LEFT.value,
            right=WidgetMargins.RIGHT.value,
            bottom=WidgetMargins.BOTTOM.value,
        )
        text_container.variables = [
            dv.IntegerVariable(name="success_visible", value=0),
            dv.IntegerVariable(name="error_visible", value=0),
            dv.StringVariable(name="error_text", value=""),
        ]

        # Success container using smarty_ui
        success_text = text_1("✅ Action completed successfully!", color="#065F46")
        success_text.font_weight = dv.DivFontWeight.MEDIUM
        success_text.line_height = 20

        success_container = HStack(
            [success_text],
            padding=12,
            background="#ECFDF5",
            corner_radius=10,
            width=dv.DivMatchParentSize(),
        )
        success_container.id = "success-container"
        success_container.visibility = Expr(
            "@{success_visible == 1 ? 'visible' : 'gone'}"
        )
        success_container.margins = dv.DivEdgeInsets(
            top=12, left=16, right=16, bottom=8
        )
        success_container.border = dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        )

        # Error container using smarty_ui
        error_icon = caption_1("⚠️")
        error_icon.font_size = 16
        error_icon.margins = dv.DivEdgeInsets(right=10)

        error_msg = text_1("@{error_text}", color="#B91C1C")
        error_msg.font_weight = dv.DivFontWeight.MEDIUM
        error_msg.line_height = 20
        error_msg.width = dv.DivMatchParentSize(weight=1)

        dismiss_error = caption_1("✕", color="#B91C1C")
        dismiss_error.font_size = 18
        dismiss_error.font_weight = dv.DivFontWeight.BOLD
        dismiss_error.paddings = dv.DivEdgeInsets(left=10, right=4)
        dismiss_error.actions = [
            dv.DivAction(
                log_id="dismiss-error",
                url="div-action://set_variable?name=error_visible&value=0",
            )
        ]

        error_container = HStack(
            [error_icon, error_msg, dismiss_error],
            padding=12,
            background="#FEF2F2",
            corner_radius=10,
            width=dv.DivMatchParentSize(),
        )
        error_container.id = "error-container"
        error_container.visibility = Expr("@{error_visible == 1 ? 'visible' : 'gone'}")
        error_container.margins = dv.DivEdgeInsets(top=12, left=16, right=16, bottom=8)
        error_container.border = dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#FECACA", width=1)
        )

        # Approve button using smarty_ui text component with actions
        approve_btn = text_1("Approve", color="#2563EB")
        approve_btn.id = "btn-approve"
        approve_btn.border = dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
        )
        approve_btn.alignment_horizontal = dv.DivAlignmentHorizontal.CENTER
        approve_btn.height = dv.DivFixedSize(value=36)
        approve_btn.paddings = dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8)
        approve_btn.margins = dv.DivEdgeInsets(right=8)
        approve_btn.actions = [
            dv.DivAction(
                url="divkit://send-request",
                log_id="btn-approve",
                typed=dv.DivActionSubmit(
                    container_id="btn-approve",
                    request=dv.DivActionSubmitRequest(
                        url=approve_link,
                        method=dv.RequestMethod.GET,
                        headers=[dv.RequestHeader(name="api-key", value=api_key)],
                    ),
                    on_success_actions=[
                        dv.DivAction(
                            log_id="approve-success",
                            url="div-action://set_variable?name=success_visible&value=1",
                        )
                    ],
                    on_fail_actions=[
                        dv.DivAction(
                            log_id="approve-error",
                            url="div-action://set_variable?name=error_visible&value=1",
                        ),
                        dv.DivAction(
                            log_id="set-error-text",
                            url="div-action://set_variable?name=error_text&value=Failed to approve request",
                        ),
                    ],
                ),
            ),
        ]

        # Reject button using smarty_ui text component with actions
        reject_btn = text_1("Reject", color="#2563EB")
        reject_btn.id = "btn-reject"
        reject_btn.border = dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
        )
        reject_btn.alignment_horizontal = dv.DivAlignmentHorizontal.CENTER
        reject_btn.height = dv.DivFixedSize(value=36)
        reject_btn.paddings = dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8)
        reject_btn.margins = dv.DivEdgeInsets(right=8)
        reject_btn.actions = [
            dv.DivAction(
                url="divkit://send-request",
                log_id="btn-reject",
                typed=dv.DivActionSubmit(
                    container_id="btn-reject",
                    request=dv.DivActionSubmitRequest(
                        url=reject_link,
                        method=dv.RequestMethod.GET,
                        headers=[dv.RequestHeader(name="api-key", value=api_key)],
                    ),
                    on_success_actions=[
                        dv.DivAction(
                            log_id="reject-success",
                            url="div-action://set_variable?name=success_visible&value=1",
                        )
                    ],
                    on_fail_actions=[
                        dv.DivAction(
                            log_id="reject-error",
                            url="div-action://set_variable?name=error_visible&value=1",
                        ),
                        dv.DivAction(
                            log_id="set-error-text",
                            url="div-action://set_variable?name=error_text&value=Failed to reject request",
                        ),
                    ],
                ),
            ),
        ]

        # Buttons container using HStack
        buttons_container = HStack([approve_btn, reject_btn])

        # Main container using VStack
        container = VStack([text_container, buttons_container])

        logger.info("Successfully built human approval UI container")
        return dv.make_div(container)

    except KeyError as e:
        logger.error(
            "Missing required key in human_approval_input",
            error=str(e),
            input_keys=list(human_approval_input.keys()),
        )
        raise
    except Exception as e:
        logger.error("Error building human approval UI", error=str(e))
        raise


class HumanApprovalRequests(FunctionStrategy):
    """Strategy for building human approval UI with fallback."""

    def build_widget_inputs(self, context):
        """Build the happy-path widget inputs (approval widget)."""
        return {
            human_approval_ui: WidgetInput(
                widget=Widget(
                    order=2,
                    type="approval_widget",
                    name="approval_widget",
                    layout="vertical",
                    fields=["approval_widget"],
                    values=[context.backend_output],
                ),
                args={
                    "human_approval_input": context.backend_output,
                    "language": context.language,
                    "api_key": context.api_key,
                    "text": context.llm_output,
                },
            ),
        }

    def execute(self, context):
        logger = context.logger_context.logger
        logger.info(
            "Starting human approval requests processing",
            chat_id=context.logger_context.chat_id,
        )
        try:
            return super().execute(context)
        except Exception as e:
            logger.error(
                "Error creating widgets, falling back to text widget only", error=str(e)
            )
            text_builder, text_input = self.make_text_input(context.llm_output)
            return self._build_and_save(context, {text_builder: text_input})


human_approval_requests = HumanApprovalRequests()
