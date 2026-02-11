from typing import Any

from pydantic import BaseModel
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
from tool_call_models.paynet import PaymentManagerCheckUpResponse
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
from datetime import datetime


class EventBase(BaseModel):
    tool_call_id: str
    user_id: str
    session_id: str
    app_name: str
    # created_at: Any


class HumanApprovalRequestEvent(EventBase):
    approve_link: str
    reject_link: str
    arguments: dict[str, Any] | None = None
    tool_name: str | None = None


class PayForHomeUtilityArguments(BaseModel):
    amount: int
    category_id: str
    supplier_id: str
    region_id: str | None = None
    payment_no: str
    payment_no1: str | None = None
    payment_no2: str | None = None
    payment_no3: str | None = None
    payment_no4: str | None = None
    supplierName: str
    homeImage: str
    homeName: str
    supplierImage: str
    checkUp: PaymentManagerCheckUpResponse


def _mask_pii(value: str) -> str:
    """Mask PII (e.g. full name) for display: E****ROV J****SHID style."""
    if not value or len(value.strip()) < 4:
        return "****"
    parts = value.strip().split()
    masked = []
    for part in parts:
        if len(part) <= 2:
            masked.append("*" * len(part))
        else:
            masked.append(part[0] + "****" + part[-1].upper())
    return " ".join(masked)


def _account_detail_row(
    label: str,
    value: str,
    mask_value: bool = False,
) -> dv.DivBase:
    """One receipt-style row: label (left), dotted line, value (right)."""
    display_value = _mask_pii(value) if mask_value else value
    label_view = caption_2(label, color="#6B7280")
    label_view.width = dv.DivWrapContentSize()

    # Dotted filler: middle dots so label and value align like the reference
    dots = text_1(" · " * 24, color="#D1D5DB")
    dots.font_size = 10
    dots.width = dv.DivMatchParentSize(weight=1)
    dots.text_alignment_horizontal = dv.DivAlignmentHorizontal.LEFT

    value_view = text_1(display_value, color="#111827")
    value_view.font_weight = dv.DivFontWeight.REGULAR
    value_view.width = dv.DivWrapContentSize()
    value_view.text_alignment_horizontal = dv.DivAlignmentHorizontal.RIGHT

    row = HStack([label_view, dots, value_view])
    row.margins = dv.DivEdgeInsets(top=10, bottom=10)
    return row


def human_approval_ui(
    human_approval_input: HumanApprovalRequestEvent,
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
            "approval_title_generic": "Iltimos, amalni tasdiqlang.",
            "approval_title_utility": "Kommunal to'lovni tasdiqlang.",
            "account_details_title": "Hisob tafsilotlari",
            "current_balance": "Joriy balans",
            "account_number": "Shaxsiy hisob",
            "region": "Hudud",
            "full_name": "F.I.O.",
            "address": "Manzil",
            "meter_reading": "Hisoblagich ko'rsatkichlari",
        },
        LanguageOptions.RUSSIAN: {
            "payment_status": "Сумма платежа",
            "currency": "cумм.",
            "payment_description": "Платеж за товары и услуги",
            "transaction_details": "Номер транзакции:",
            "date": "Время перевода:",
            "sender": "Отправитель:",
            "receiver": "Получатель:",
            "approval_title_generic": "Пожалуйста, подтвердите действие.",
            "approval_title_utility": "Подтвердите коммунальный платёж.",
            "account_details_title": "Детали счета",
            "current_balance": "Текущий баланс",
            "account_number": "Лицевой счет",
            "region": "Регион",
            "full_name": "ФИО",
            "address": "Адрес",
            "meter_reading": "Показания счетчика",
        },
        LanguageOptions.ENGLISH: {
            "payment_status": "Payment amount",
            "currency": "USD",
            "payment_description": "Payment for goods and services",
            "transaction_details": "Transaction number:",
            "date": "Transfer time:",
            "sender": "Sender:",
            "receiver": "Receiver:",
            "approval_title_generic": "Please approve this action.",
            "approval_title_utility": "Please confirm the utility payment.",
            "account_details_title": "Account details",
            "current_balance": "Current balance",
            "account_number": "Account number",
            "region": "Region",
            "full_name": "Full name",
            "address": "Address",
            "meter_reading": "Meter reading",
        },
    }

    try:
        approve_link = human_approval_input.approve_link
        reject_link = human_approval_input.reject_link

        logger.info(
            "Generated approval links",
            approve_link_length=len(approve_link),
            reject_link_length=len(reject_link),
        )

        # Build approval info text using smarty_ui (do not expose IDs)
        localized_texts = texts_map.get(language, texts_map[LanguageOptions.ENGLISH])

        if human_approval_input.tool_name == "pay_for_home_utility_wrapper":
            header_text = localized_texts.get(
                "approval_title_utility", localized_texts["approval_title_generic"]
            )
        else:
            header_text = localized_texts["approval_title_generic"]

        info_text = text_1(header_text, color="#111133")
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

        # Optional details container for specific tools (e.g. pay_for_home_utility_wrapper)
        utility_details_container = None

        if (
            human_approval_input.tool_name == "pay_for_home_utility_wrapper"
            and human_approval_input.arguments
        ):
            try:
                arguments = PayForHomeUtilityArguments.model_validate(
                    human_approval_input.arguments
                )
            except Exception as e:
                logger.warning(
                    "PayForHomeUtilityArguments validation failed, skipping account-details view",
                    error=str(e),
                )
                arguments = None

            if arguments is not None:
                # Localized labels for account-details view (receipt style)
                account_detail_labels = {
                    LanguageOptions.UZBEK: {
                        "title": "Hisob tafsilotlari",
                        "current_balance": "Joriy balans",
                        "account_number": "Shaxsiy hisob",
                        "supplier": "Ta'minotchi",
                        "service": "Xizmat",
                        "region": "Hudud",
                        "address": "Manzil",
                        "meter_reading": "Hisoblagich",
                    },
                    LanguageOptions.RUSSIAN: {
                        "title": "Детали счета",
                        "current_balance": "Текущий баланс",
                        "account_number": "Лицевой счет",
                        "supplier": "Поставщик",
                        "service": "Услуга",
                        "region": "Регион",
                        "address": "Адрес",
                        "meter_reading": "Показания счетчика",
                    },
                    LanguageOptions.ENGLISH: {
                        "title": "Account details",
                        "current_balance": "Current balance",
                        "account_number": "Account number",
                        "supplier": "Supplier",
                        "service": "Service",
                        "region": "Region",
                        "address": "Address",
                        "meter_reading": "Meter reading",
                    },
                }
                ad_labels = account_detail_labels.get(
                    language, account_detail_labels[LanguageOptions.ENGLISH]
                )
                currency = localized_texts.get(
                    "currency", texts_map[LanguageOptions.ENGLISH]["currency"]
                )
                details_children: list[dv.DivBase] = []

                # Handle bar (swipe hint)
                handle = text_1("\u2007", color="#E5E7EB")
                handle.width = dv.DivFixedSize(value=36)
                handle.height = dv.DivFixedSize(value=4)
                handle.background = [dv.DivSolidBackground(color="#E5E7EB")]
                handle.border = dv.DivBorder(corner_radius=2)
                handle.margins = dv.DivEdgeInsets(bottom=16)
                details_children.append(handle)

                # Title: "Детали счета"
                details_title = title_2(ad_labels["title"], color="#111827")
                details_title.font_weight = dv.DivFontWeight.BOLD
                details_title.margins = dv.DivEdgeInsets(bottom=4)
                details_children.append(details_title)

                checkup_data = arguments.checkUp.data
                response_by_name: dict[str, str] = {
                    item.name.strip().lower(): item.value
                    for item in checkup_data.response
                }
                shown_keys = set(response_by_name.keys())

                def _should_mask(name: str, type_str: str) -> bool:
                    n = (name or "").strip().lower()
                    t = (type_str or "").strip().lower()
                    return (
                        "фио" in n
                        or "fio" in n
                        or "full name" in n
                        or "full_name" in n
                        or "name" in t
                        or "full_name" in t
                        or "fio" in t
                    )

                # 1) Current balance (from checkup balance or payment amount)
                # balance_value = str(
                #     (checkup_data.balance if checkup_data.balance is not None else "0")
                # )
                # balance_str = balance_value
                # details_children.append(
                #     _account_detail_row(
                #         ad_labels["current_balance"],
                #         f"{balance_str} {currency}",
                #         mask_value=False,
                #     )
                # )

                # 2) Rows from checkup response (sorted by order)
                for item in sorted(checkup_data.response, key=lambda x: x.order):
                    if not item.value:
                        continue
                    mask = _should_mask(item.name, item.type)
                    details_children.append(
                        _account_detail_row(
                            item.name,
                            item.value,
                            mask_value=mask,
                        )
                    )

                # 3) Supplemental from arguments if not already in checkup response
                def _add_supplement(label_key: str, value: str | None):
                    if not value:
                        return
                    details_children.append(
                        _account_detail_row(
                            ad_labels[label_key],
                            str(value),
                            mask_value=False,
                        )
                    )

                def _response_has(fragments: list[str]) -> bool:
                    return any(f in shown_keys for f in fragments)

                # Account number (payment_no) - often shown with copy in reference
                if not _response_has(
                    [
                        "лицевой счет",
                        "account number",
                        "shaxsiy hisob",
                        "номер платежа",
                        "to'lov raqami",
                    ]
                ):
                    _add_supplement("account_number", arguments.payment_no)
                if not _response_has(["поставщик", "supplier", "ta'minotchi"]):
                    _add_supplement("supplier", arguments.supplierName)
                if arguments.region_id and not _response_has(
                    ["регион", "region", "hudud"]
                ):
                    _add_supplement("region", arguments.region_id)
                if arguments.homeName:
                    svc_label = ad_labels.get("service", "Service")
                    details_children.append(
                        _account_detail_row(
                            svc_label, arguments.homeName, mask_value=False
                        )
                    )

                if details_children:
                    utility_details_container = VStack(
                        details_children,
                        padding=20,
                        background="#FFFFFF",
                        corner_radius=16,
                        width=dv.DivMatchParentSize(),
                    )
                    utility_details_container.border = dv.DivBorder(
                        corner_radius=16,
                        stroke=dv.DivStroke(color="#E5E7EB", width=1),
                    )
                    utility_details_container.margins = dv.DivEdgeInsets(
                        top=12,
                        left=WidgetMargins.LEFT.value,
                        right=WidgetMargins.RIGHT.value,
                        bottom=0,
                    )

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
        children = [text_container]
        if "utility_details_container" in locals() and utility_details_container:
            children.append(utility_details_container)
        children.append(buttons_container)

        container = VStack(children)

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

    def build_widget_inputs(self, context: Context):
        """Build the happy-path widget inputs (approval widget)."""
        logger.info(
            "Context Infor for Human Approval",
            backend_output=context.backend_output,
        )
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
                    "human_approval_input": HumanApprovalRequestEvent.model_validate(
                        context.backend_output["human_approval_event"]
                    ),
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
