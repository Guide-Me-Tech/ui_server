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

from conf import logger
from functions_to_format.functions.general.const_values import (
    LanguageOptions,
    WidgetMargins,
)
import structlog
from models.context import Context
import pydivkit as dv

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

        #  "tool_call_id": "tool_send_money_to_someone_via_card_wrapper_jD3yQhOEG53QTSWiKUEf",
        #         "user_id": "60005982",
        #         "session_id": "a96d3fa0-a3c8-43cd-9090-f55afb285ff9",
        #         "app_name": "smarty",
        #         "created_at": {
        #             "seconds": 1770202179
        #         },

        # based on the Human Approval Requests
        # first lets make some button for approve and reject actually
        text_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.VERTICAL,
            background=[dv.DivSolidBackground(color="#F8FAFF")],  # light bluish-white
            border=dv.DivBorder(corner_radius=16),
            paddings=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
            items=[
                dv.DivText(
                    text="Please approve the action. \n"
                    + "user_id: "
                    + human_approval_input["human_approval_event"]["user_id"]
                    + "\n"
                    + "session_id: "
                    + human_approval_input["human_approval_event"]["session_id"]
                    + "\n"
                    + "app_name: "
                    + human_approval_input["human_approval_event"]["app_name"]
                    + "\n"
                    + "\n",
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
        buttons_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            items=[
                dv.DivText(
                    text="Approve",
                    id="btn-approve",
                    font_size=14,
                    text_color="#2563EB",
                    border=dv.DivBorder(
                        corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                    ),
                    alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    height=dv.DivFixedSize(value=36),
                    paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                    margins=dv.DivEdgeInsets(right=8),
                    actions=[
                        dv.DivAction(
                            url="divkit://send-request",
                            log_id="btn-approve",
                            typed=dv.DivActionSubmit(
                                container_id="btn-approve",
                                request=dv.DivActionSubmitRequest(
                                    url=approve_link,
                                    method=dv.RequestMethod.GET,
                                    headers=[
                                        dv.RequestHeader(name="api-key", value=api_key)
                                    ],
                                ),
                            ),
                        ),
                    ],
                ),
                dv.DivText(
                    text="Reject",
                    id="btn-reject",
                    font_size=14,
                    text_color="#2563EB",
                    border=dv.DivBorder(
                        corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                    ),
                    alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    height=dv.DivFixedSize(value=36),
                    paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                    margins=dv.DivEdgeInsets(right=8),
                    actions=[
                        dv.DivAction(
                            url="divkit://send-request",
                            log_id="btn-reject",
                            typed=dv.DivActionSubmit(
                                container_id="btn-reject",
                                request=dv.DivActionSubmitRequest(
                                    url=reject_link,
                                    method=dv.RequestMethod.GET,
                                    headers=[
                                        dv.RequestHeader(name="api-key", value=api_key)
                                    ],
                                ),
                            ),
                        ),
                    ],
                ),
            ],
        )
        container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.VERTICAL,
            items=[text_container, buttons_container],
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
                "text": llm_output,
            },
        )

        logger.info("human_approval_requests - widget created successfully")

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
