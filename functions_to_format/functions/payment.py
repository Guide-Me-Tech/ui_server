import json

from functions_to_format.functions.balance import get_home_balances
from functions_to_format.functions.functions import chatbot_answer

from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    ButtonsWidget,
    build_text_widget,
    build_buttons_row,
    WidgetInput,
    create_feedback_variables,
    create_success_actions,
    create_failure_actions,
    create_success_container,
    create_error_container,
)
from .general.utils import save_builder_output
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import pydivkit as dv
from pydivkit.core import Expr
from models.build import BuildOutput
from tool_call_models.cards import CardsByPhoneNumberResponse, CardInfoByPhoneNumber
from tool_call_models.paynet import (
    CategoriesResponse,
    PaymentManagerPaymentResponse,
    SupplierByCategoryResponse,
    Supplier,
    Category,
)
from tool_call_models.cards import CardInfoByCardNumberResponse
from conf import logger
from functions_to_format.functions.general.const_values import LanguageOptions
import structlog
from models.context import Context, LoggerContext


# Feedback texts for payment actions
PAYMENT_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "card_selected": "Карта выбрана",
        "category_selected": "Категория выбрана",
        "supplier_selected": "Поставщик выбран",
        "selection_error": "Ошибка выбора",
    },
    LanguageOptions.ENGLISH: {
        "card_selected": "Card selected",
        "category_selected": "Category selected",
        "supplier_selected": "Supplier selected",
        "selection_error": "Selection error",
    },
    LanguageOptions.UZBEK: {
        "card_selected": "Karta tanlandi",
        "category_selected": "Kategoriya tanlandi",
        "supplier_selected": "Ta'minotchi tanlandi",
        "selection_error": "Tanlash xatosi",
    },
}


def build_pay_for_home_utility_ui(
    payment_response: PaymentManagerPaymentResponse,
    language: LanguageOptions = LanguageOptions.UZBEK,
):
    """Build a payment success card UI using pydivkit"""

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

    # get receiver name  ---- receiver name is the item in data.response where item["order"] == 1
    receiver_name = ""
    for item in payment_response.data.response:
        if item.order == 1:
            receiver_name = item.value
            break

    # Create payment details items from response
    payment_items = []
    for item in payment_response.data.response:
        payment_items.append(
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivText(
                        text=item.name,
                        text_color="#666666",
                        font_size=14,
                        font_weight=dv.DivFontWeight.REGULAR,
                        width=dv.DivWrapContentSize(),
                        margins=dv.DivEdgeInsets(right=8),
                    ),
                    dv.DivText(
                        text=item.value,
                        text_color="#000000",
                        font_size=14,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        width=dv.DivMatchParentSize(),
                        text_alignment_horizontal=dv.DivAlignmentHorizontal.END,
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=12),
            )
        )

    # Create success card matching the image design
    success_card = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[
            dv.DivSolidBackground(
                color="#FFFFFF",
            )
        ],
        border=dv.DivBorder(
            corner_radius=16,
        ),
        paddings=dv.DivEdgeInsets(left=24, top=32, right=24, bottom=32),
        margins=dv.DivEdgeInsets(left=16, top=16, right=16, bottom=16),
        items=[
            # Success checkmark icon
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivContainer(
                        background=[
                            dv.DivSolidBackground(
                                color="#E8F5E8",
                            )
                        ],
                        border=dv.DivBorder(
                            corner_radius=50,
                        ),
                        width=dv.DivFixedSize(value=80),
                        height=dv.DivFixedSize(value=80),
                        items=[
                            dv.DivText(
                                text="✓",
                                text_color="#4CAF50",
                                font_size=36,
                                font_weight=dv.DivFontWeight.BOLD,
                                text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            ),
                        ],
                    ),
                ],
                content_alignment_horizontal=dv.DivContentAlignmentHorizontal.CENTER,
                margins=dv.DivEdgeInsets(bottom=24),
            ),
            # Payment success title
            dv.DivText(
                text=texts_map[language]["payment_status"],
                text_color="#666666",
                font_size=16,
                font_weight=dv.DivFontWeight.REGULAR,
                text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                margins=dv.DivEdgeInsets(bottom=8),
            ),
            # Amount
            dv.DivText(
                text=f"{payment_response.additional.amount if payment_response.additional else '0'} {texts_map[language]['currency']}",
                text_color="#000000",
                font_size=32,
                font_weight=dv.DivFontWeight.BOLD,
                text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                margins=dv.DivEdgeInsets(bottom=8),
            ),
            # Service description
            dv.DivContainer(
                background=[
                    dv.DivSolidBackground(
                        color="#E8F5E8",
                    )
                ],
                border=dv.DivBorder(
                    corner_radius=8,
                ),
                paddings=dv.DivEdgeInsets(left=12, top=8, right=12, bottom=8),
                margins=dv.DivEdgeInsets(bottom=32),
                items=[
                    dv.DivText(
                        text=texts_map[language]["payment_description"],
                        text_color="#4CAF50",
                        font_size=14,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    ),
                ],
            ),
            # Transaction details
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivText(
                        text=texts_map[language]["transaction_details"],
                        text_color="#666666",
                        font_size=14,
                        font_weight=dv.DivFontWeight.REGULAR,
                        width=dv.DivWrapContentSize(),
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=8),
            ),
            # Separator line
            dv.DivSeparator(
                delimiter_style=dv.DivSeparatorDelimiterStyle(
                    color="#E0E0E0",
                ),
                margins=dv.DivEdgeInsets(bottom=16),
            ),
            # Date
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivText(
                        text=texts_map[language]["date"],
                        text_color="#666666",
                        font_size=14,
                        font_weight=dv.DivFontWeight.REGULAR,
                        width=dv.DivWrapContentSize(),
                    ),
                    dv.DivText(
                        text=payment_response.additional.date
                        if payment_response.additional
                        else "",
                        text_color="#000000",
                        font_size=14,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        width=dv.DivMatchParentSize(),
                        text_alignment_horizontal=dv.DivAlignmentHorizontal.END,
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=16),
            ),
            # Recipient
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivText(
                        text=texts_map[language]["sender"],
                        text_color="#666666",
                        font_size=14,
                        font_weight=dv.DivFontWeight.REGULAR,
                        width=dv.DivWrapContentSize(),
                    ),
                    dv.DivContainer(
                        orientation=dv.DivContainerOrientation.VERTICAL,
                        width=dv.DivMatchParentSize(),
                        items=[
                            dv.DivText(
                                text=payment_response.additional.sender_name
                                if payment_response.additional
                                else "",
                                text_color="#000000",
                                font_size=14,
                                font_weight=dv.DivFontWeight.MEDIUM,
                                text_alignment_horizontal=dv.DivAlignmentHorizontal.END,
                            ),
                            dv.DivText(
                                text=payment_response.additional.sender_masked_pan
                                if payment_response.additional
                                else "**** **** **** ****",
                                text_color="#666666",
                                font_size=12,
                                font_weight=dv.DivFontWeight.REGULAR,
                                text_alignment_horizontal=dv.DivAlignmentHorizontal.END,
                            ),
                        ],
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=16),
            ),
            # Receiver
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivText(
                        text=texts_map[language]["receiver"],
                        text_color="#666666",
                        font_size=14,
                        font_weight=dv.DivFontWeight.REGULAR,
                        width=dv.DivWrapContentSize(),
                    ),
                    dv.DivText(
                        text=receiver_name,
                        text_color="#000000",
                        font_size=14,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        width=dv.DivMatchParentSize(),
                        text_alignment_horizontal=dv.DivAlignmentHorizontal.END,
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=16),
            ),
        ],
    )

    return dv.make_div(success_card)


def pay_for_home_utility(context: Context) -> BuildOutput:
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    inp = {}

    try:
        backend_output = PaymentManagerPaymentResponse.model_validate(backend_output)
        payment_status_widget = Widget(
            order=2,
            type="payment_status_widget",
            name="payment_status_widget",
            layout="vertical",
            fields=["payment_status"],
            values=[backend_output.model_dump()],
        )
        inp[build_pay_for_home_utility_ui] = WidgetInput(
            widget=payment_status_widget,
            args={"payment_response": backend_output},
        )

        logger.info("pay_for_home_utility")

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

    except Exception as e:
        inp[build_text_widget] = WidgetInput(
            widget=text_widget,
            args={
                "text": llm_output,
            },
        )

    widgets = add_ui_to_widget(
        inp,
        version,
    )
    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )

    save_builder_output(context, output)
    return output


# ============================================================================
# Receiver by Card Models and UI
# ============================================================================

class ReceiverByCardResponse(BaseModel):
    """Model for receiver information retrieved by card number."""
    processingSystem: str
    iconMini: Optional[str] = None
    isFound: bool
    maskedPan: str
    errorMessage: Optional[str] = None
    icon: Optional[str] = None
    fullName: Optional[str] = None
    errorCode: Optional[str] = None
    token: Optional[str] = None


# Feedback texts for money transfer actions
TRANSFER_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "receiver_found": "Получатель найден",
        "receiver_not_found": "Получатель не найден",
        "transfer_success": "Перевод выполнен успешно!",
        "transfer_error": "Ошибка перевода",
        "confirm_transfer": "Подтвердить перевод",
        "cancel": "Отмена",
        "amount": "Сумма",
        "recipient": "Получатель",
        "card": "Карта",
        "currency": "сум",
        "send": "Отправить",
        "processing": "Обработка...",
    },
    LanguageOptions.ENGLISH: {
        "receiver_found": "Recipient found",
        "receiver_not_found": "Recipient not found",
        "transfer_success": "Transfer completed successfully!",
        "transfer_error": "Transfer failed",
        "confirm_transfer": "Confirm transfer",
        "cancel": "Cancel",
        "amount": "Amount",
        "recipient": "Recipient",
        "card": "Card",
        "currency": "UZS",
        "send": "Send",
        "processing": "Processing...",
    },
    LanguageOptions.UZBEK: {
        "receiver_found": "Qabul qiluvchi topildi",
        "receiver_not_found": "Qabul qiluvchi topilmadi",
        "transfer_success": "O'tkazma muvaffaqiyatli bajarildi!",
        "transfer_error": "O'tkazma xatosi",
        "confirm_transfer": "O'tkazmani tasdiqlash",
        "cancel": "Bekor qilish",
        "amount": "Summa",
        "recipient": "Qabul qiluvchi",
        "card": "Karta",
        "currency": "so'm",
        "send": "Yuborish",
        "processing": "Qayta ishlanmoqda...",
    },
}


def get_processing_system_icon(processing_system: str) -> str:
    """Get icon URL for a processing system."""
    icons = {
        "VISA": "https://upload.wikimedia.org/wikipedia/commons/thumb/5/5e/Visa_Inc._logo.svg/200px-Visa_Inc._logo.svg.png",
        "MASTERCARD": "https://upload.wikimedia.org/wikipedia/commons/thumb/2/2a/Mastercard-logo.svg/200px-Mastercard-logo.svg.png",
        "HUMO": "https://humocard.uz/bitrix/templates/main/img/card2.png",
        "UZCARD": "https://uzcard.uz/upload/images/logo.png",
    }
    return icons.get(processing_system.upper(), "https://via.placeholder.com/48x32")


def build_receiver_by_card_ui(
    receiver_data: ReceiverByCardResponse,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build UI for displaying receiver information retrieved by card number.
    
    Args:
        receiver_data: Receiver information from backend
        language: Language for localization
        
    Returns:
        DivKit JSON for the receiver card UI
    """
    feedback_texts = TRANSFER_FEEDBACK_TEXTS.get(language, TRANSFER_FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    
    # Determine icon URL
    icon_url = receiver_data.icon or get_processing_system_icon(receiver_data.processingSystem)
    
    if not receiver_data.isFound:
        # Error state - receiver not found
        error_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.VERTICAL,
            background=[dv.DivSolidBackground(color="#FEF2F2")],
            border=dv.DivBorder(
                corner_radius=16, stroke=dv.DivStroke(color="#FECACA", width=1)
            ),
            paddings=dv.DivEdgeInsets(left=20, right=20, top=20, bottom=20),
            margins=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
            items=[
                dv.DivContainer(
                    orientation=dv.DivContainerOrientation.HORIZONTAL,
                    alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    items=[
                        dv.DivText(
                            text="❌",
                            font_size=32,
                            margins=dv.DivEdgeInsets(right=12),
                        ),
                        dv.DivText(
                            text=feedback_texts["receiver_not_found"],
                            font_size=18,
                            font_weight=dv.DivFontWeight.BOLD,
                            text_color="#B91C1C",
                        ),
                    ],
                    margins=dv.DivEdgeInsets(bottom=12),
                ),
                dv.DivText(
                    text=receiver_data.errorMessage or feedback_texts["transfer_error"],
                    font_size=14,
                    text_color="#7F1D1D",
                    text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                ),
            ],
        )
        return dv.make_div(error_container)
    
    # Success state - receiver found
    receiver_card = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(
            corner_radius=16, stroke=dv.DivStroke(color="#E5E7EB", width=1)
        ),
        paddings=dv.DivEdgeInsets(left=20, right=20, top=20, bottom=20),
        margins=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
        variables=[
            dv.IntegerVariable(name="receiver_card_success", value=0),
            dv.IntegerVariable(name="receiver_card_error", value=0),
        ],
        items=[
            # Header with success indicator
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                items=[
                    dv.DivContainer(
                        background=[dv.DivSolidBackground(color="#ECFDF5")],
                        border=dv.DivBorder(corner_radius=20),
                        width=dv.DivFixedSize(value=40),
                        height=dv.DivFixedSize(value=40),
                        items=[
                            dv.DivText(
                                text="✓",
                                font_size=20,
                                font_weight=dv.DivFontWeight.BOLD,
                                text_color="#059669",
                                text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            ),
                        ],
                        margins=dv.DivEdgeInsets(right=12),
                    ),
                    dv.DivText(
                        text=feedback_texts["receiver_found"],
                        font_size=16,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        text_color="#059669",
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=20),
            ),
            # Receiver info card
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                background=[dv.DivSolidBackground(color="#F9FAFB")],
                border=dv.DivBorder(corner_radius=12),
                paddings=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
                items=[
                    # Card icon/avatar
                    dv.DivContainer(
                        background=[dv.DivSolidBackground(color="#EBF5FF")],
                        border=dv.DivBorder(corner_radius=24),
                        width=dv.DivFixedSize(value=48),
                        height=dv.DivFixedSize(value=48),
                        items=[
                            dv.DivImage(
                                image_url=icon_url,
                                width=dv.DivFixedSize(value=32),
                                height=dv.DivFixedSize(value=20),
                                scale=dv.DivImageScale.FIT,
                                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            ),
                        ],
                        margins=dv.DivEdgeInsets(right=16),
                    ),
                    # Receiver details
                    dv.DivContainer(
                        orientation=dv.DivContainerOrientation.VERTICAL,
                        items=[
                            dv.DivText(
                                text=receiver_data.fullName or "Unknown",
                                font_size=16,
                                font_weight=dv.DivFontWeight.BOLD,
                                text_color="#111827",
                                margins=dv.DivEdgeInsets(bottom=4),
                            ),
                            dv.DivContainer(
                                orientation=dv.DivContainerOrientation.HORIZONTAL,
                                items=[
                                    dv.DivText(
                                        text=receiver_data.processingSystem,
                                        font_size=13,
                                        font_weight=dv.DivFontWeight.MEDIUM,
                                        text_color="#3B82F6",
                                    ),
                                    dv.DivText(
                                        text=f"  •  {receiver_data.maskedPan}",
                                        font_size=13,
                                        text_color="#6B7280",
                                    ),
                                ],
                            ),
                        ],
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=16),
            ),
            # Success feedback container
            dv.DivContainer(
                id="receiver-card-success",
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                visibility=Expr("@{receiver_card_success == 1 ? 'visible' : 'gone'}"),
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                width=dv.DivMatchParentSize(),
                margins=dv.DivEdgeInsets(top=8, bottom=8),
                paddings=dv.DivEdgeInsets(top=10, bottom=10, left=12, right=12),
                background=[dv.DivSolidBackground(color="#ECFDF5")],
                border=dv.DivBorder(
                    corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
                ),
                items=[
                    dv.DivText(
                        text="✅",
                        font_size=14,
                        margins=dv.DivEdgeInsets(right=8),
                    ),
                    dv.DivText(
                        text=feedback_texts["receiver_found"],
                        font_size=13,
                        text_color="#065F46",
                        font_weight=dv.DivFontWeight.MEDIUM,
                        width=dv.DivMatchParentSize(weight=1),
                    ),
                    dv.DivText(
                        text="✕",
                        font_size=16,
                        text_color="#065F46",
                        font_weight=dv.DivFontWeight.BOLD,
                        paddings=dv.DivEdgeInsets(left=8),
                        actions=[
                            dv.DivAction(
                                log_id="dismiss-receiver-card-success",
                                url="div-action://set_variable?name=receiver_card_success&value=0",
                            )
                        ],
                    ),
                ],
            ),
            # Action button - Confirm/Select
            dv.DivText(
                text=feedback_texts["confirm_transfer"],
                font_size=15,
                font_weight=dv.DivFontWeight.MEDIUM,
                text_color="#FFFFFF",
                background=[dv.DivSolidBackground(color="#3B82F6")],
                border=dv.DivBorder(corner_radius=10),
                height=dv.DivFixedSize(value=44),
                width=dv.DivMatchParentSize(),
                text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                margins=dv.DivEdgeInsets(top=8),
                actions=[
                    dv.DivAction(
                        log_id="confirm_receiver_selection",
                        url="divkit://confirm_receiver",
                        payload={
                            "token": receiver_data.token,
                            "fullName": receiver_data.fullName,
                            "maskedPan": receiver_data.maskedPan,
                            "processingSystem": receiver_data.processingSystem,
                        },
                    ),
                    dv.DivAction(
                        log_id="confirm_receiver_success",
                        url="div-action://set_variable?name=receiver_card_success&value=1",
                    ),
                ],
            ),
        ],
    )
    
    div = dv.make_div(receiver_card)
    with open("logs/json/build_receiver_by_card_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_receiver_by_card(context: Context) -> BuildOutput:
    """
    Process receiver information from card lookup and create UI widgets.
    
    Args:
        context: Context object containing backend_output, version, language, etc.
        
    Returns:
        BuildOutput with receiver card widget
    """
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger
    
    logger.info("get_receiver_by_card", backend_output=backend_output)
    
    try:
        receiver_data = ReceiverByCardResponse(**backend_output)
    except Exception as e:
        logger.error("Error parsing receiver data", error=str(e))
        receiver_data = ReceiverByCardResponse(
            processingSystem="UNKNOWN",
            isFound=False,
            maskedPan="****",
            errorMessage=str(e),
        )
    
    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )
    
    receiver_widget = Widget(
        name="receiver_by_card_widget",
        type="receiver_by_card_widget",
        order=2,
        layout="vertical",
        fields=["processingSystem", "isFound", "maskedPan", "fullName", "token"],
        values=[receiver_data.model_dump(exclude_none=True)],
    )
    
    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
            build_receiver_by_card_ui: WidgetInput(
                widget=receiver_widget,
                args={
                    "receiver_data": receiver_data,
                    "language": language,
                },
            ),
        },
        version,
    )
    
    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


# ============================================================================
# Send Money Transfer UI
# ============================================================================

def build_send_money_ui(
    amount: int,
    receiver_name: str,
    masked_pan: str,
    processing_system: str,
    token: str,
    chat_id: str,
    api_key: str,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build UI for confirming and sending money transfer.
    
    Args:
        amount: Transfer amount in minor units (e.g., tiyin)
        receiver_name: Recipient's full name
        masked_pan: Masked card PAN
        processing_system: Card processing system (VISA, HUMO, etc.)
        token: Transfer token for API
        chat_id: Chat ID for API call
        api_key: API key for authorization
        language: Language for localization
        
    Returns:
        DivKit JSON for the transfer confirmation UI
    """
    feedback_texts = TRANSFER_FEEDBACK_TEXTS.get(language, TRANSFER_FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    icon_url = get_processing_system_icon(processing_system)
    
    # Format amount
    formatted_amount = f"{amount:,}".replace(",", " ")
    
    transfer_card = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(
            corner_radius=20, stroke=dv.DivStroke(color="#E5E7EB", width=1)
        ),
        paddings=dv.DivEdgeInsets(left=24, right=24, top=24, bottom=24),
        margins=dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16),
        variables=[
            dv.IntegerVariable(name="transfer_success", value=0),
            dv.IntegerVariable(name="transfer_error", value=0),
            dv.IntegerVariable(name="transfer_loading", value=0),
        ],
        id="transfer_container",
        items=[
            # Amount header
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.VERTICAL,
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                items=[
                    dv.DivText(
                        text=feedback_texts["amount"],
                        font_size=14,
                        text_color="#6B7280",
                        margins=dv.DivEdgeInsets(bottom=8),
                    ),
                    dv.DivText(
                        text=f"{formatted_amount} {feedback_texts['currency']}",
                        font_size=32,
                        font_weight=dv.DivFontWeight.BOLD,
                        text_color="#111827",
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=24),
            ),
            # Divider
            dv.DivSeparator(
                delimiter_style=dv.DivSeparatorDelimiterStyle(color="#E5E7EB"),
                margins=dv.DivEdgeInsets(bottom=20),
            ),
            # Recipient section
            dv.DivText(
                text=feedback_texts["recipient"],
                font_size=12,
                font_weight=dv.DivFontWeight.MEDIUM,
                text_color="#9CA3AF",
                margins=dv.DivEdgeInsets(bottom=12),
            ),
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                background=[dv.DivSolidBackground(color="#F9FAFB")],
                border=dv.DivBorder(corner_radius=12),
                paddings=dv.DivEdgeInsets(left=16, right=16, top=14, bottom=14),
                items=[
                    # Card icon
                    dv.DivContainer(
                        background=[dv.DivSolidBackground(color="#EBF5FF")],
                        border=dv.DivBorder(corner_radius=20),
                        width=dv.DivFixedSize(value=40),
                        height=dv.DivFixedSize(value=40),
                        items=[
                            dv.DivImage(
                                image_url=icon_url,
                                width=dv.DivFixedSize(value=28),
                                height=dv.DivFixedSize(value=18),
                                scale=dv.DivImageScale.FIT,
                                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                alignment_vertical=dv.DivAlignmentVertical.CENTER,
                            ),
                        ],
                        margins=dv.DivEdgeInsets(right=14),
                    ),
                    # Recipient details
                    dv.DivContainer(
                        orientation=dv.DivContainerOrientation.VERTICAL,
                        items=[
                            dv.DivText(
                                text=receiver_name,
                                font_size=15,
                                font_weight=dv.DivFontWeight.MEDIUM,
                                text_color="#111827",
                            ),
                            dv.DivContainer(
                                orientation=dv.DivContainerOrientation.HORIZONTAL,
                                items=[
                                    dv.DivText(
                                        text=processing_system,
                                        font_size=13,
                                        font_weight=dv.DivFontWeight.MEDIUM,
                                        text_color="#3B82F6",
                                    ),
                                    dv.DivText(
                                        text=f"  •  {masked_pan}",
                                        font_size=13,
                                        text_color="#6B7280",
                                    ),
                                ],
                                margins=dv.DivEdgeInsets(top=2),
                            ),
                        ],
                    ),
                ],
                margins=dv.DivEdgeInsets(bottom=20),
            ),
            # Success feedback container
            dv.DivContainer(
                id="transfer-success-container",
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                visibility=Expr("@{transfer_success == 1 ? 'visible' : 'gone'}"),
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                width=dv.DivMatchParentSize(),
                margins=dv.DivEdgeInsets(bottom=16),
                paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
                background=[dv.DivSolidBackground(color="#ECFDF5")],
                border=dv.DivBorder(
                    corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
                ),
                items=[
                    dv.DivText(
                        text="✅",
                        font_size=16,
                        margins=dv.DivEdgeInsets(right=10),
                    ),
                    dv.DivText(
                        text=feedback_texts["transfer_success"],
                        font_size=14,
                        text_color="#065F46",
                        font_weight=dv.DivFontWeight.MEDIUM,
                        width=dv.DivMatchParentSize(weight=1),
                    ),
                    dv.DivText(
                        text="✕",
                        font_size=18,
                        text_color="#065F46",
                        font_weight=dv.DivFontWeight.BOLD,
                        paddings=dv.DivEdgeInsets(left=10),
                        actions=[
                            dv.DivAction(
                                log_id="dismiss-transfer-success",
                                url="div-action://set_variable?name=transfer_success&value=0",
                            )
                        ],
                    ),
                ],
            ),
            # Error feedback container
            dv.DivContainer(
                id="transfer-error-container",
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                visibility=Expr("@{transfer_error == 1 ? 'visible' : 'gone'}"),
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                width=dv.DivMatchParentSize(),
                margins=dv.DivEdgeInsets(bottom=16),
                paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
                background=[dv.DivSolidBackground(color="#FEF2F2")],
                border=dv.DivBorder(
                    corner_radius=10, stroke=dv.DivStroke(color="#FECACA", width=1)
                ),
                items=[
                    dv.DivText(
                        text="⚠️",
                        font_size=16,
                        margins=dv.DivEdgeInsets(right=10),
                    ),
                    dv.DivText(
                        text=feedback_texts["transfer_error"],
                        font_size=14,
                        text_color="#B91C1C",
                        font_weight=dv.DivFontWeight.MEDIUM,
                        width=dv.DivMatchParentSize(weight=1),
                    ),
                    dv.DivText(
                        text="✕",
                        font_size=18,
                        text_color="#B91C1C",
                        font_weight=dv.DivFontWeight.BOLD,
                        paddings=dv.DivEdgeInsets(left=10),
                        actions=[
                            dv.DivAction(
                                log_id="dismiss-transfer-error",
                                url="div-action://set_variable?name=transfer_error&value=0",
                            )
                        ],
                    ),
                ],
            ),
            # Loading indicator
            dv.DivContainer(
                id="transfer-loading-container",
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                visibility=Expr("@{transfer_loading == 1 ? 'visible' : 'gone'}"),
                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                width=dv.DivMatchParentSize(),
                margins=dv.DivEdgeInsets(bottom=16),
                paddings=dv.DivEdgeInsets(top=12, bottom=12, left=14, right=14),
                background=[dv.DivSolidBackground(color="#F3F4F6")],
                border=dv.DivBorder(
                    corner_radius=10, stroke=dv.DivStroke(color="#D1D5DB", width=1)
                ),
                items=[
                    dv.DivText(
                        text="⏳",
                        font_size=16,
                        margins=dv.DivEdgeInsets(right=10),
                    ),
                    dv.DivText(
                        text=feedback_texts["processing"],
                        font_size=14,
                        text_color="#4B5563",
                        font_weight=dv.DivFontWeight.MEDIUM,
                    ),
                ],
            ),
            # Buttons row
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                width=dv.DivMatchParentSize(),
                items=[
                    # Cancel button
                    dv.DivText(
                        text=feedback_texts["cancel"],
                        font_size=15,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        text_color="#6B7280",
                        background=[dv.DivSolidBackground(color="#F3F4F6")],
                        border=dv.DivBorder(corner_radius=10),
                        height=dv.DivFixedSize(value=48),
                        width=dv.DivMatchParentSize(),
                        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                        text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                        margins=dv.DivEdgeInsets(right=8),
                        actions=[
                            dv.DivAction(
                                log_id="cancel_transfer",
                                url="divkit://cancel_transfer",
                                payload={"action": "cancel"},
                            ),
                        ],
                    ),
                    # Send button with submit action
                    dv.DivText(
                        id="send_money_btn",
                        text=feedback_texts["send"],
                        font_size=15,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        text_color="#FFFFFF",
                        background=[dv.DivSolidBackground(color="#3B82F6")],
                        border=dv.DivBorder(corner_radius=10),
                        height=dv.DivFixedSize(value=48),
                        width=dv.DivMatchParentSize(),
                        text_alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                        text_alignment_vertical=dv.DivAlignmentVertical.CENTER,
                        margins=dv.DivEdgeInsets(left=8),
                        actions=[
                            dv.DivAction(
                                log_id="send_money_action",
                                url="divkit://send-request",
                                typed=dv.DivActionSubmit(
                                    container_id="transfer_container",
                                    request=dv.DivActionSubmitRequest(
                                        url=f"https://smarty.smartbank.uz/chat/v3/tools/call?function_name=execute_card_transfer&chat_id={chat_id}&arguments={json.dumps({'token': token, 'amount': amount})}",
                                        method=dv.RequestMethod.POST,
                                        headers=[
                                            dv.RequestHeader(name="api-key", value=api_key)
                                        ],
                                    ),
                                    on_success_actions=[
                                        dv.DivAction(
                                            log_id="transfer-success-show",
                                            url="div-action://set_variable?name=transfer_success&value=1",
                                        ),
                                        dv.DivAction(
                                            log_id="transfer-loading-hide",
                                            url="div-action://set_variable?name=transfer_loading&value=0",
                                        ),
                                        dv.DivAction(
                                            log_id="transfer-error-hide",
                                            url="div-action://set_variable?name=transfer_error&value=0",
                                        ),
                                    ],
                                    on_fail_actions=[
                                        dv.DivAction(
                                            log_id="transfer-error-show",
                                            url="div-action://set_variable?name=transfer_error&value=1",
                                        ),
                                        dv.DivAction(
                                            log_id="transfer-loading-hide-error",
                                            url="div-action://set_variable?name=transfer_loading&value=0",
                                        ),
                                        dv.DivAction(
                                            log_id="transfer-success-hide",
                                            url="div-action://set_variable?name=transfer_success&value=0",
                                        ),
                                    ],
                                ),
                                payload={
                                    "token": token,
                                    "amount": amount,
                                    "receiver_name": receiver_name,
                                    "masked_pan": masked_pan,
                                },
                            ),
                            # Show loading
                            dv.DivAction(
                                log_id="show-loading",
                                url="div-action://set_variable?name=transfer_loading&value=1",
                            ),
                        ],
                    ),
                ],
            ),
        ],
    )
    
    div = dv.make_div(transfer_card)
    with open("logs/json/build_send_money_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def send_money_to_someone_via_card(context: Context) -> BuildOutput:
    """
    Process money transfer and create UI widgets for confirmation/result.
    
    Args:
        context: Context object containing llm_output, backend_output, version, etc.
        
    Returns:
        BuildOutput with transfer confirmation widget
    """
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    logger.info("send_money_to_someone_via_card", backend_output=backend_output)
    
    # Extract transfer details from backend_output
    amount = backend_output.get("amount", 0)
    receiver_name = backend_output.get("fullName") or backend_output.get("card_owner_name", "Unknown")
    masked_pan = backend_output.get("maskedPan") or backend_output.get("marked_card_pan", "****")
    processing_system = backend_output.get("processingSystem", "UNKNOWN")
    token = backend_output.get("token") or backend_output.get("to_card_id", "")
    
    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )
    
    transfer_widget = Widget(
        name="send_money_widget",
        type="send_money_widget",
        order=2,
        layout="vertical",
        fields=[
            "amount",
            "receiver_name",
            "masked_pan",
            "processing_system",
            "token",
        ],
        values=[{
            "amount": amount,
            "receiver_name": receiver_name,
            "masked_pan": masked_pan,
            "processing_system": processing_system,
            "token": token,
        }],
    )
    
    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
            build_send_money_ui: WidgetInput(
                widget=transfer_widget,
                args={
                    "amount": amount,
                    "receiver_name": receiver_name,
                    "masked_pan": masked_pan,
                    "processing_system": processing_system,
                    "token": token,
                    "chat_id": chat_id,
                    "api_key": api_key,
                    "language": language,
                },
            ),
        },
        version,
    )
    
    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_number_by_receiver_name(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    logger.info("get_number_by_receiver_name")
    output = []
    # backend_output_processed = []
    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    get_contacts_widget = Widget(
        name="get_contacts_widget",
        type="get_contacts_widget",
        order=2,
        layout="vertical",
        fields=["receiver_name"],
        values=[{"receiver_name": backend_output["names"]}],
    )

    buttons = ButtonsWidget(
        order=3,
        values=[{"text": "cancel"}],
    )

    names = (
        ",".join(backend_output["names"])
        if isinstance(backend_output["names"], list)
        else backend_output["names"]
    )

    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={
                    "text": f"Contactlaringiz orasidan {names} ismini qidirishimiz kerak. Qidiraylikmi ?"
                },
            ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={
                    "button_texts": ["cancel", "search"],
                    "receiver_name": names,
                    "language": language,
                },
            ),
        },
        version,
    )

    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_number_by_reciver_number_ui(receiver_name: Union[str, List[str]]):
    logger.info("get_number_by_reciver_number_ui")
    if isinstance(receiver_name, list):
        search_contact_action = dv.DivAction(
            log_id="search_contact",
            url=f"divkit://search_contact?name={receiver_name}",  # Custom scheme the iOS app will catch
            payload={"name": receiver_name},  # Optional: structured access
        )
    else:
        search_contact_action = dv.DivAction(
            log_id="search_contact",
            url=f"divkit://search_contact?name=[{receiver_name}]",  # Custom scheme the iOS app will catch
            payload={"name": [receiver_name]},  # Optional: structured access
        )

    # Main container
    main_container = dv.DivContainer(
        items=[
            dv.DivContainer(
                items=[],
                action=search_contact_action,
                visibility=dv.DivVisibility.INVISIBLE,
            )
        ]
    )
    div = dv.make_div(main_container)
    with open("logs/json/build_get_number_by_reciver_number_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
        logger.info("Saved to build_get_number_by_reciver_number_ui.json", div=div)
    logger.info("get_number_by_reciver_number_ui done")
    return div


def get_receiver_id_by_receiver_phone_number(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    output = []
    # backend_output_processed = []
    backend_output = CardsByPhoneNumberResponse(**backend_output)

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    get_contacts_widget = Widget(
        name="get_contacts_widget",
        type="get_contacts_widget",
        order=2,
        layout="vertical",
        fields=["receiver_name"],
        values=[x.model_dump() for x in backend_output.cards],
    )

    buttons = ButtonsWidget(
        order=3,
        values=[{"text": "cancel"}],
    )

    widgets = add_ui_to_widget(
        {
            get_receiver_id_by_receiver_phone_number_ui: WidgetInput(
                widget=get_contacts_widget,
                args={"cards": backend_output.cards},
            ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={
                    "button_texts": ["cancel"],
                    "language": language,
                },
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )

    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_receiver_id_by_receiver_phone_number_ui(
    cards: List[CardInfoByPhoneNumber],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Builds a UI showing a list of cards for a receiver with feedback handling.

    Args:
        cards: List of card information
        language: Language for localization

    Returns:
        DivKit JSON for the card selection UI
    """
    feedback_texts = PAYMENT_FEEDBACK_TEXTS.get(
        language, PAYMENT_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    card_items = []
    for idx, card in enumerate(cards, 1):
        card_items.append(
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=[
                    dv.DivContainer(
                        width=dv.DivFixedSize(value=36),
                        height=dv.DivFixedSize(value=36),
                        background=[dv.DivSolidBackground(color="#F3F6FA")],
                        border=dv.DivBorder(
                            stroke=dv.DivStroke(
                                color="#E5E7EB",
                                width=1,
                            ),
                            corner_radius=18,
                        ),
                        items=[
                            dv.DivContainer(
                                width=dv.DivFixedSize(value=36),
                                height=dv.DivFixedSize(value=36),
                                alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                alignment_vertical=dv.DivAlignmentVertical.CENTER,
                                items=[
                                    dv.DivText(
                                        text=str(idx),
                                        font_size=18,
                                        font_weight=dv.DivFontWeight.MEDIUM,
                                        text_color="#3B82F6",
                                        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                                        alignment_vertical=dv.DivAlignmentVertical.CENTER,
                                        margins=dv.DivEdgeInsets(
                                            top=7, left=12, right=12, bottom=7
                                        ),
                                    )
                                ],
                            )
                        ],
                        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                        alignment_vertical=dv.DivAlignmentVertical.CENTER,
                        margins=dv.DivEdgeInsets(right=12),
                    ),
                    dv.DivContainer(
                        orientation=dv.DivContainerOrientation.VERTICAL,
                        items=[
                            dv.DivText(
                                text=card.name,
                                font_size=16,
                                font_weight=dv.DivFontWeight.MEDIUM,
                                text_color="#222222",
                                line_height=20,
                            ),
                            dv.DivContainer(
                                orientation=dv.DivContainerOrientation.HORIZONTAL,
                                items=[
                                    dv.DivText(
                                        text=card.processing,
                                        font_size=15,
                                        font_weight=dv.DivFontWeight.BOLD,
                                        text_color="#1976D2",
                                        line_height=18,
                                        letter_spacing=0.2,
                                    ),
                                    dv.DivText(
                                        text="  ••  " + str(card.mask),
                                        font_size=15,
                                        text_color="#374151",
                                        line_height=18,
                                        margins=dv.DivEdgeInsets(left=1),
                                        max_lines=1,
                                        text_alignment_horizontal=dv.DivAlignmentHorizontal.LEFT,
                                    ),
                                ],
                                margins=dv.DivEdgeInsets(top=2),
                                width=dv.DivWrapContentSize(),
                            ),
                        ],
                    ),
                ],
                paddings=dv.DivEdgeInsets(bottom=16, left=16, right=16, top=16),
                background=[dv.DivSolidBackground(color="#FFFFFF")],
                margins=dv.DivEdgeInsets(bottom=0 if idx == len(cards) else 8),
                actions=[
                    # Main selection action
                    dv.DivAction(
                        log_id=f"select_card_{idx}",
                        url=f"divkit://select?card_id={idx}",
                        payload={
                            "card_id": card.pan,
                            "card_name": card.name,
                            "card_processing": card.processing,
                            "card_mask": card.mask,
                        },
                    ),
                    # Success feedback action
                    dv.DivAction(
                        log_id=f"select_card_{idx}_success",
                        url="div-action://set_variable?name=card_selection_success&value=1",
                    ),
                ],
            )
        )
        # Add divider except after last item
        if idx < len(cards):
            card_items.append(
                dv.DivSeparator(
                    delimiter_style=dv.DivSeparatorDelimiterStyle(
                        color="#F3F6FA",
                    ),
                    width=dv.DivFixedSize(value=1),
                    margins=dv.DivEdgeInsets(left=52, right=0),
                )
            )

    # Success feedback container
    success_container = dv.DivContainer(
        id="card-selection-success",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{card_selection_success == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=12, right=12, bottom=4),
        paddings=dv.DivEdgeInsets(top=10, bottom=10, left=12, right=12),
        background=[dv.DivSolidBackground(color="#ECFDF5")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=14,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=feedback_texts["card_selected"],
                font_size=13,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=16,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-card-selection-success",
                        url="div-action://set_variable?name=card_selection_success&value=0",
                    )
                ],
            ),
        ],
    )

    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        variables=[
            dv.IntegerVariable(name="card_selection_success", value=0),
            dv.IntegerVariable(name="card_selection_error", value=0),
        ],
        items=[
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.VERTICAL,
                items=card_items,
                background=[dv.DivSolidBackground(color="#F9FAFB")],
                border=dv.DivBorder(
                    stroke=dv.DivStroke(
                        color="#E5E7EB",
                        width=1,
                    ),
                    corner_radius=16,
                ),
                paddings=dv.DivEdgeInsets(bottom=0, left=0, right=0, top=0),
                margins=dv.DivEdgeInsets(bottom=0, left=12, right=12, top=12),
            ),
            success_container,
        ],
    )

    div = dv.make_div(main_container)
    with open(
        "logs/json/build_get_receiver_id_by_receiver_phone_number_ui.json", "w"
    ) as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_categories(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    backend_output = CategoriesResponse(**backend_output)
    backend_output_processed: List[Category] = backend_output.payload

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    categories_widget = Widget(
        name="payments_list_item_widget",
        type="payments_list_item_widget",
        order=2,
        layout="vertical",
        fields=["id", "name", "image_url"],
        values=[category.model_dump() for category in backend_output_processed],
    )

    buttons = ButtonsWidget(
        order=3,
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            build_get_categories_ui: WidgetInput(
                widget=categories_widget,
                args={"categories": backend_output_processed},
            ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={
                    "button_texts": ["cancel"],
                    "language": language,
                },
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    output = BuildOutput(
        widgets_count=3,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def build_get_categories_ui(
    categories: List[Category],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build categories UI with feedback handling for category selection.

    Args:
        categories: List of category objects
        language: Language for localization

    Returns:
        DivKit JSON for the categories UI
    """
    feedback_texts = PAYMENT_FEEDBACK_TEXTS.get(
        language, PAYMENT_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    category_items = []
    for idx, category in enumerate(categories):
        item_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            width=dv.DivFixedSize(value=303),
            items=[
                dv.DivImage(
                    image_url=category.s3Url,
                    width=dv.DivFixedSize(value=24),
                    height=dv.DivFixedSize(value=24),
                ),
                dv.DivText(
                    text=category.name,
                    font_size=16,
                    font_weight=dv.DivFontWeight.REGULAR,
                    text_color="#000000",
                    margins=dv.DivEdgeInsets(left=14),
                ),
            ],
            alignment_vertical=dv.DivAlignmentVertical.CENTER,
            actions=[
                # Main selection action
                dv.DivAction(
                    log_id=f"category_{category.id}_selected",
                    payload={
                        "category_id": category.id,
                        "category_name": category.name,
                    },
                    url=f"divkit://action?type=select_category&id={category.id}&name={category.name}",
                ),
                # Success feedback action
                dv.DivAction(
                    log_id=f"category_{category.id}_success",
                    url="div-action://set_variable?name=category_selection_success&value=1",
                ),
            ],
        )
        category_items.append(item_container)

        # Add separator with consistent spacing
        if idx < len(categories) - 1:
            category_items.append(
                dv.DivSeparator(
                    delimiter_style=dv.DivSeparatorDelimiterStyle(color="#E0E0E0"),
                    margins=dv.DivEdgeInsets(top=12, bottom=12),
                )
            )

    # Success feedback container
    success_container = dv.DivContainer(
        id="category-selection-success",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{category_selection_success == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, bottom=8),
        paddings=dv.DivEdgeInsets(top=10, bottom=10, left=12, right=12),
        background=[dv.DivSolidBackground(color="#ECFDF5")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=14,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=feedback_texts["category_selected"],
                font_size=13,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=16,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-category-selection-success",
                        url="div-action://set_variable?name=category_selection_success&value=0",
                    )
                ],
            ),
        ],
    )

    category_items.append(success_container)

    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivFixedSize(value=343),
        height=dv.DivFixedSize(value=958),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        items=category_items,
        border=dv.DivBorder(corner_radius=20),
        paddings=dv.DivEdgeInsets(top=16, right=16, bottom=8, left=16),
        margins=dv.DivEdgeInsets(left=16, top=657),
        variables=[
            dv.IntegerVariable(name="category_selection_success", value=0),
        ],
    )

    div = dv.make_div(main_container)
    with open("logs/json/build_get_categories_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_suppliers_by_category(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    backend_output = SupplierByCategoryResponse(**backend_output)
    backend_output_processed: List[Supplier] = backend_output.payload

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    suppliers_widget = Widget(
        name="payments_list_item_widget",
        type="payments_list_item_widget",
        order=2,
        layout="vertical",
        fields=["id", "name", "image_url", "category_id"],
        values=[supplier.model_dump() for supplier in backend_output_processed],
    )
    buttons_widget = ButtonsWidget(
        order=3,
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            get_suppliers_by_category_ui: WidgetInput(
                widget=suppliers_widget,
                args={"suppliers": backend_output_processed},
            ),
            build_buttons_row: WidgetInput(
                widget=buttons_widget,
                args={
                    "button_texts": ["cancel"],
                    "language": language,
                },
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    output = BuildOutput(
        widgets_count=3,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def get_suppliers_by_category_ui(
    suppliers: List[Supplier],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build suppliers UI with feedback handling for supplier selection.

    Args:
        suppliers: List of supplier objects
        language: Language for localization

    Returns:
        DivKit JSON for the suppliers UI
    """
    feedback_texts = PAYMENT_FEEDBACK_TEXTS.get(
        language, PAYMENT_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    supplier_items = []
    for idx, supplier in enumerate(suppliers):
        item_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            width=dv.DivMatchParentSize(),
            height=dv.DivWrapContentSize(),
            alignment_vertical=dv.DivAlignmentVertical.CENTER,
            background=[dv.DivSolidBackground(color="#EBF2FA")],
            paddings=dv.DivEdgeInsets(top=16, bottom=16, left=16, right=16),
            items=[
                dv.DivImage(
                    image_url=supplier.s3Url,
                    width=dv.DivFixedSize(value=32),
                    height=dv.DivFixedSize(value=32),
                    margins=dv.DivEdgeInsets(right=12),
                    scale=dv.DivImageScale.FIT,
                    border=dv.DivBorder(corner_radius=16),
                ),
                dv.DivText(
                    text=supplier.name,
                    font_size=16,
                    font_weight=dv.DivFontWeight.REGULAR,
                    text_color="#000000",
                ),
            ],
            actions=[
                # Main selection action
                dv.DivAction(
                    log_id=f"supplier_{supplier.id}_selected",
                    payload={
                        "supplier_id": supplier.id,
                        "supplier_name": supplier.name,
                    },
                    url=f"divkit://open_supplier?id={supplier.id}&name={supplier.name}",
                ),
                # Success feedback action
                dv.DivAction(
                    log_id=f"supplier_{supplier.id}_success",
                    url="div-action://set_variable?name=supplier_selection_success&value=1",
                ),
            ],
        )
        supplier_items.append(item_container)

        if idx < len(suppliers) - 1:
            supplier_items.append(
                dv.DivSeparator(
                    delimiter_style=dv.DivSeparatorDelimiterStyle(color="#E0E0E0"),
                    margins=dv.DivEdgeInsets(left=60, right=16),
                )
            )

    # Success feedback container
    success_container = dv.DivContainer(
        id="supplier-selection-success",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{supplier_selection_success == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, left=8, right=8, bottom=4),
        paddings=dv.DivEdgeInsets(top=10, bottom=10, left=12, right=12),
        background=[dv.DivSolidBackground(color="#ECFDF5")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=14,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=feedback_texts["supplier_selected"],
                font_size=13,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=16,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-supplier-selection-success",
                        url="div-action://set_variable?name=supplier_selection_success&value=0",
                    )
                ],
            ),
        ],
    )

    supplier_items.append(success_container)

    main_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        width=dv.DivMatchParentSize(),
        height=dv.DivWrapContentSize(),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        items=supplier_items,
        border=dv.DivBorder(corner_radius=12),
        margins=dv.DivEdgeInsets(top=8, bottom=8, left=8, right=8),
        variables=[
            dv.IntegerVariable(name="supplier_selection_success", value=0),
        ],
    )

    div = dv.make_div(main_container)
    with open("logs/json/build_get_suppliers_by_category_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


class Field(BaseModel):
    identName: Optional[str] = None
    name: Optional[str] = None
    order: Optional[int] = None
    type: Optional[str] = None
    pattern: Optional[str] = None
    minValue: Optional[int] = None
    maxValue: Optional[int] = None
    fieldSize: Optional[int] = None
    isMain: Optional[bool] = None
    valueList: List[str] = []


def get_fields_of_supplier(context) -> BuildOutput:
    from models.context import Context

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    logger.info("get_fields_of_supplier")
    backend_output_processed: List[Field] = []
    for i, field in enumerate(backend_output["payload"]["fieldList"]):
        backend_output_processed.append(
            Field(
                identName=field["identName"],
                name=field["name"],
                order=field["order"],
                type=field["type"],
                pattern=field["pattern"],
                minValue=field["minValue"],
                maxValue=field["maxValue"],
                fieldSize=field["fieldSize"],
                isMain=field["isMain"],
                valueList=[str(field["valueList"])],
            )
        )
    if llm_output:
        text_widget = TextWidget(
            order=1,
            values=[{"text": llm_output}],
        )

    fields_widget = Widget(
        name="fields_widget",
        type="fields_widget",
        order=2,
        layout="vertical",
        fields=[
            "identName",
            "name",
            "order",
            "type",
            "pattern",
            "minValue",
            "maxValue",
            "fieldSize",
            "isMain",
            "valueList",
        ],
        values=[field.model_dump() for field in backend_output_processed],
    )

    button_widget = ButtonsWidget(
        order=3,
        values=[
            {"text": "Cancel", "action": "cancel"},
        ],
    )

    widgets = add_ui_to_widget(
        {
            get_fields_of_supplier_ui: WidgetInput(
                widget=fields_widget,
                args={"fields": backend_output_processed},
            ),
            build_buttons_row: WidgetInput(
                widget=button_widget,
                args={
                    "button_texts": [
                        "cancel",
                    ],
                    "language": language,
                },
            ),
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )
    if len(llm_output) > 0:
        output = BuildOutput(
            widgets_count=3,
            widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
        )
    else:
        output = BuildOutput(
            widgets_count=2,
            widgets=[widget.model_dump(exclude_none=True) for widget in widgets[:2]],
        )
    save_builder_output(context, output)
    return output


def get_fields_of_supplier_ui(fields: List[Field]):
    logger.info("get_fields_of_supplier_ui", fields=fields)
    return
    raise NotImplementedError()
    div = dv.make_div(
        dv.DivContainer(
            orientation="vertical",
            width=dv.DivFixedSize(value=343),
            height=dv.DivFixedSize(value=555),
            margins=dv.DivEdgeInsets(top=110, left=16),
            items=[
                dv.DivContainer(
                    orientation="vertical",
                    width=dv.DivMatchParentSize(),
                    items=[
                        dv.DivInput(
                            hint_text=str(
                                field.name
                            ),  # Convert to string to ensure not None
                            font_size=16,
                            text_color="#1A1A1A",
                            hint_color="#999999",
                            margins=dv.DivEdgeInsets(bottom=16),
                            keyboard_type="text",  # Ensure text input type
                        )
                        for field in fields
                    ],
                )
            ],
        )
    )
    with open("logs/json/build_get_fields_of_supplier_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def get_home_utility_suppliers(context) -> BuildOutput:
    return get_home_balances(context)


if __name__ == "__main__":
    # check get_contacts with action first
    # output = get_receiver_id_by_receiver_phone_number(
    #     llm_output="", backend_output={"receiver_name": "Aslon"}, version="v3"
    # )
    # with open("logs/json/test_response.json", "w") as f:
    #     json.dump(output.model_dump(), f)
    data = [
        {
            "pan": "kkkkkkxxxxxxyyyyyy",
            "name": "Aslon",
            "processing": "HUMO",
            "mask": "*************1234",
        },
        {
            "pan": "kkkkkkxxxxxxyyasdfafsdfyyyy",
            "name": "Aslon",
            "processing": "HUMO",
            "mask": "*************1235",
        },
        {
            "pan": "kkkkkkxxxxxxyyasdfafsdfyyyy",
            "name": "Aslon",
            "processing": "HUMO",
            "mask": "*************1236",
        },
    ]
    context = Context(
        llm_output="Hello world",
        backend_output=CardsByPhoneNumberResponse.model_validate(data).model_dump(),
        version="v3",
        language=LanguageOptions.UZBEK,
        api_key="test",
        logger_context=LoggerContext(
            chat_id="test",
            logger=logger,
        ),
    )
    output = get_receiver_id_by_receiver_phone_number(context=context)
    with open("logs/json/test_response.json", "w") as f:
        json.dump(output.model_dump(), f, ensure_ascii=False, indent=2)
