from typing import Any
from functions_to_format.functions.buttons import build_buttons_row
from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    build_text_widget,
    WidgetInput,
)
from .general.utils import save_builder_output
from models.build import BuildOutput
from tool_call_models.paynet import (
    PaymentManagerPaymentResponse,
)
from conf import logger
from functions_to_format.functions.general.const_values import LanguageOptions
import structlog
from models.context import Context
import pydivkit as dv

logger: structlog.stdlib.BoundLogger = structlog.get_logger(__name__)


def human_approval_ui(
    human_approval_input: dict[str, Any],
    language: LanguageOptions = LanguageOptions.UZBEK,
    api_key: str = "",
):
    """Build a payment success card UI using pydivkit"""
    logger.info(
        "Building human approval UI", language=language, has_api_key=bool(api_key)
    )

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
        approve_link = (
            human_approval_input["human_approval_event"]["approve_link"]
            + f"&api-key={api_key}"
        )
        reject_link = (
            human_approval_input["human_approval_event"]["reject_link"]
            + f"&api-key={api_key}"
        )

        logger.info(
            "Generated approval links",
            approve_link_length=len(approve_link),
            reject_link_length=len(reject_link),
        )

        # based on the Human Approval Requests
        # first lets make some button for approve and reject actually
        container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            items=[
                dv.DivText(
                    text="Approve",
                    font_size=14,
                    text_color="#2563EB",
                    border=dv.DivBorder(
                        corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                    ),
                    alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    height=dv.DivFixedSize(value=36),
                    paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                    margins=dv.DivEdgeInsets(right=8),
                    action=dv.DivAction(
                        log_id="btn-approve",
                        url=approve_link,
                    ),
                ),
                dv.DivText(
                    text="Reject",
                    font_size=14,
                    text_color="#2563EB",
                    border=dv.DivBorder(
                        corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                    ),
                    alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    height=dv.DivFixedSize(value=36),
                    paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                    margins=dv.DivEdgeInsets(right=8),
                    action=dv.DivAction(
                        log_id="btn-reject",
                        url=reject_link,
                    ),
                ),
            ],
        )

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


def human_approval_requests(context: Context) -> BuildOutput:
    context.logger_context.logger.info(
        "Starting human approval requests processing",
        chat_id=context.logger_context.chat_id,
    )

    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    logger.info(
        "Extracted context values",
        llm_output_length=len(llm_output) if llm_output else 0,
        backend_output_keys=list(backend_output.keys())
        if isinstance(backend_output, dict)
        else "not_dict",
        version=version,
        language=language,
    )

    inp = {}

    try:
        logger.info("Creating human approval widget")
        human_approval_widget = Widget(
            order=2,
            type="approval_widget",
            name="approval_widget",
            layout="vertical",
            fields=["approval_widget"],
            values=[backend_output],
        )
        inp[human_approval_ui] = WidgetInput(
            widget=human_approval_widget,
            args={
                "human_approval_input": backend_output,
                "language": language,
                "api_key": api_key,
            },
        )

        logger.info("human_approval_requests - widget created successfully")

        logger.info("Creating text widget", llm_output=llm_output)
        text_widget = TextWidget(
            order=1,
            values=[{"text": llm_output}],
        )
        inp[build_text_widget] = WidgetInput(
            widget=text_widget,
            args={
                "text": llm_output,
            },
        )
        logger.info("Text widget created successfully")

    except Exception as e:
        logger.error(
            "Error creating widgets, falling back to text widget only", error=str(e)
        )
        text_widget = TextWidget(
            order=1,
            values=[{"text": llm_output}],
        )
        inp[build_text_widget] = WidgetInput(
            widget=text_widget,
            args={
                "text": llm_output,
            },
        )

    logger.info("Adding UI to widgets", widget_count=len(inp))
    widgets = add_ui_to_widget(
        inp,
        version,
    )

    logger.info("Widgets processed", final_widget_count=len(widgets))

    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )

    logger.info("Saving builder output")
    save_builder_output(context, output)

    logger.info(
        "Human approval requests processing completed successfully",
        output_widget_count=output.widgets_count,
    )
    return output
