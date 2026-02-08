import json
from datetime import datetime

from .base_strategy import FunctionStrategy
from .general import (
    Widget,
    ButtonsWidget,
    WidgetInput,
)
from .buttons import build_buttons_row
from pydantic import BaseModel
from typing import List, Dict, Any, Optional, Union
import pydivkit as dv
from pydivkit.core import Expr
from tool_call_models.cards import CardsByPhoneNumberResponse, CardInfoByPhoneNumber

from conf import logger
from functions_to_format.functions.general.const_values import LanguageOptions
from models.context import Context, LoggerContext
from smarty_ui.blocks.send_money_widget import send_money_widget


# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    title_1,
    title_2,
    text_1,
)
from smarty_ui.composites import assistant_bubble

# Import smarty_ui blocks for ready-made components
from smarty_ui.blocks import (
    receiver_cards_list,
    contacts_list,
    cards_own_list,
    transaction_status_widget,
    transaction_success_widget,
    transaction_failed_widget,
)
from smarty_ui.blocks.contacts_list import search_for_contacts
from smarty_ui.primitives import smarty_button, smarty_button_filled
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
    Build UI for displaying receiver information retrieved by card number using smarty_ui.

    Args:
        receiver_data: Receiver information from backend
        language: Language for localization

    Returns:
        DivKit JSON for the receiver card UI
    """
    feedback_texts = TRANSFER_FEEDBACK_TEXTS.get(
        language, TRANSFER_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    # Determine icon URL
    icon_url = receiver_data.icon or get_processing_system_icon(
        receiver_data.processingSystem
    )

    if not receiver_data.isFound:
        # Error state - receiver not found using smarty_ui
        error_icon = title_1("❌")
        error_icon.margins = dv.DivEdgeInsets(right=12)

        error_title = title_2(feedback_texts["receiver_not_found"], color="#B91C1C")

        error_header = HStack([error_icon, error_title], align_h="center")
        error_header.margins = dv.DivEdgeInsets(bottom=12)

        error_message = text_1(
            receiver_data.errorMessage or feedback_texts["transfer_error"],
            color="#7F1D1D",
        )
        error_message.text_alignment_horizontal = dv.DivAlignmentHorizontal.CENTER

        error_container = VStack(
            [error_header, error_message],
            padding=20,
            background="#FEF2F2",
            corner_radius=16,
        )
        error_container.border = dv.DivBorder(
            corner_radius=16, stroke=dv.DivStroke(color="#FECACA", width=1)
        )
        error_container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

        return dv.make_div(error_container)

    # Success state - receiver found using smarty_ui receiver_cards_list
    # Build receiver card data for the component
    receiver_card_data = [
        {
            "holder_name": receiver_data.fullName or "Unknown",
            "card_last_digits": receiver_data.maskedPan[-4:]
            if receiver_data.maskedPan
            else "****",
            "provider_logo_url": icon_url,
            "action_url": f"divkit://confirm_receiver?token={receiver_data.token}&fullName={receiver_data.fullName}&maskedPan={receiver_data.maskedPan}&processingSystem={receiver_data.processingSystem}",
        }
    ]

    # Use smarty_ui receiver_cards_list component
    cards_widget = receiver_cards_list(receiver_card_data)

    # Success header using smarty_ui
    success_icon = text_1("✓", color="#059669")
    success_icon.font_weight = dv.DivFontWeight.BOLD
    success_icon.font_size = 20
    success_icon.width = dv.DivFixedSize(value=40)
    success_icon.height = dv.DivFixedSize(value=40)
    success_icon.background = [dv.DivSolidBackground(color="#ECFDF5")]
    success_icon.border = dv.DivBorder(corner_radius=20)
    success_icon.text_alignment_horizontal = dv.DivAlignmentHorizontal.CENTER
    success_icon.text_alignment_vertical = dv.DivAlignmentVertical.CENTER
    success_icon.margins = dv.DivEdgeInsets(right=12)

    success_text = text_1(feedback_texts["receiver_found"], color="#059669")
    success_text.font_weight = dv.DivFontWeight.MEDIUM

    success_header = HStack(
        [success_icon, success_text], align_v="center", align_h="center"
    )
    success_header.margins = dv.DivEdgeInsets(bottom=16)

    # Confirm button using smarty_button_filled
    confirm_btn = smarty_button_filled(
        text=feedback_texts["confirm_transfer"],
        action_url=f"divkit://confirm_receiver?token={receiver_data.token}",
    )
    confirm_btn.width = dv.DivMatchParentSize()
    confirm_btn.height = dv.DivFixedSize(value=44)
    confirm_btn.border = dv.DivBorder(corner_radius=10)
    confirm_btn.actions = [
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
    ]
    confirm_btn.margins = dv.DivEdgeInsets(top=16)

    # Main container using VStack
    main_container = VStack(
        [success_header, cards_widget, confirm_btn],
        padding=20,
        background="#FFFFFF",
        corner_radius=16,
    )
    main_container.border = dv.DivBorder(
        corner_radius=16, stroke=dv.DivStroke(color="#E5E7EB", width=1)
    )
    main_container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(main_container)
    with open("logs/json/build_receiver_by_card_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


class GetReceiverByCard(FunctionStrategy):
    """Strategy for receiver by card UI."""

    def build_widget_inputs(self, context):
        logger = context.logger_context.logger
        logger.info("get_receiver_by_card", backend_output=context.backend_output)
        try:
            receiver_data = ReceiverByCardResponse(**context.backend_output)
        except Exception as e:
            logger.error("Error parsing receiver data", error=str(e))
            receiver_data = ReceiverByCardResponse(
                processingSystem="UNKNOWN",
                isFound=False,
                maskedPan="****",
                errorMessage=str(e),
            )
        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            text_builder: text_input,
            build_receiver_by_card_ui: WidgetInput(
                widget=Widget(
                    name="receiver_by_card_widget",
                    type="receiver_by_card_widget",
                    order=2,
                    layout="vertical",
                    fields=[
                        "processingSystem",
                        "isFound",
                        "maskedPan",
                        "fullName",
                        "token",
                    ],
                    values=[receiver_data.model_dump(exclude_none=True)],
                ),
                args={"receiver_data": receiver_data, "language": context.language},
            ),
        }


get_receiver_by_card = GetReceiverByCard()


# ============================================================================
# Send Money Transfer UI
# ============================================================================


def build_send_money_ui(
    recipient_name: str,
    source_card_name: str,
    amount: str,
    *,
    recipient_card_digits: str | None = None,
    source_card_digits: str | None = None,
    recipient_icon_url: str | None = None,
    source_card_icon_url: str | None = None,
    wallet_icon_url: str | None = None,
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

    currency = TRANSFER_FEEDBACK_TEXTS.get(
        language, TRANSFER_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )["currency"]
    button_text = TRANSFER_FEEDBACK_TEXTS.get(
        language, TRANSFER_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )["confirm_transfer"]
    action_url = f"divkit://confirm_transfer?token=xxxx"

    return dv.make_div(
        send_money_widget(
            amount=str(amount),
            recipient_name=recipient_name,
            source_card_name=source_card_name,
            recipient_card_digits=recipient_card_digits,
            source_card_digits=source_card_digits,
            recipient_icon_url=recipient_icon_url,
            source_card_icon_url=source_card_icon_url,
            wallet_icon_url=wallet_icon_url,
            currency=currency,
            button_text=button_text,
            action_url=action_url,
        )
    )


class SendMoneyToSomeoneViaCard(FunctionStrategy):
    """Strategy for money transfer confirmation UI."""

    def build_widget_inputs(self, context):
        bo = context.backend_output
        context.logger_context.logger.info(
            "send_money_to_someone_via_card", backend_output=bo
        )
        amount = bo.get("amount", 0)
        recipient_name = bo.get("fullName") or bo.get("card_owner_name", "Unknown")
        recipient_card_digits = bo.get("maskedPan") or bo.get("marked_card_pan", "****")
        recipient_icon_url = bo.get("icon") or bo.get("card_icon", "****")

        source_card_name = bo.get("card_name") or bo.get("card_owner_name", "Unknown")
        source_card_digits = bo.get("maskedPan") or bo.get("marked_card_pan", "****")
        source_card_icon_url = bo.get("icon") or bo.get("card_icon", "****")

        masked_pan = bo.get("maskedPan") or bo.get("marked_card_pan", "****")
        processing_system = bo.get("processingSystem", "UNKNOWN")
        token = bo.get("token") or bo.get("to_card_id", "")

        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            text_builder: text_input,
            build_send_money_ui: WidgetInput(
                widget=Widget(
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
                    values=[
                        {
                            "amount": 1000,
                            "recipient_name": recipient_name,
                            "source_card_name": source_card_name,
                            "recipient_card_digits": recipient_card_digits,
                            "source_card_digits": source_card_digits,
                            "recipient_icon_url": recipient_icon_url,
                            "source_card_icon_url": source_card_icon_url,
                            "masked_pan": masked_pan,
                            "processing_system": processing_system,
                            "token": token,
                        }
                    ],
                ),
                args={
                    "recipient_name": recipient_name,
                    "source_card_name": source_card_name,
                    "amount": 0,
                    "recipient_card_digits": recipient_card_digits,
                    "source_card_digits": source_card_digits,
                    "recipient_icon_url": recipient_icon_url,
                    "source_card_icon_url": source_card_icon_url,
                },
            ),
        }


send_money_to_someone_via_card = SendMoneyToSomeoneViaCard()


def get_number_by_reciver_name_ui(
    receiver_name: Union[str, List[str]],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
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

    texts_map = {
        LanguageOptions.RUSSIAN: {
            "search_contact": f"Мне нужно найти контакты для {', '.join(receiver_name)}. Согласны ли вы на поиск?",
        },
        LanguageOptions.ENGLISH: {
            "search_contact": f"I need to search contacts for {', '.join(receiver_name)}. Do you approve to search ?",
        },
        LanguageOptions.UZBEK: {
            "search_contact": f"Men {', '.join(receiver_name)} nomli kontaktlarni topishim kerak. Qidirishga ruxsat bera olami?",
        },
    }

    search_contact_text = texts_map.get(language, texts_map[LanguageOptions.RUSSIAN])[
        "search_contact"
    ]

    search_button = smarty_button(
        text="Search",
        action_url=search_contact_action,
    )
    cancel_button = smarty_button(
        text="Cancel",
        action_url=f"divkit://cancel?name={receiver_name}",
    )

    # Main container
    main_container = dv.DivContainer(
        items=[
            assistant_bubble(
                text=search_contact_text,
            ),
            HStack([search_button, cancel_button]),
        ]
    )
    div = dv.make_div(main_container)
    with open("logs/json/build_get_number_by_reciver_number_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
        logger.info("Saved to build_get_number_by_reciver_number_ui.json", div=div)
    logger.info("get_number_by_reciver_number_ui done")
    return div


class GetNumberByReceiverName(FunctionStrategy):
    """Strategy for receiver name search UI using smarty_ui search_for_contacts."""

    def build_widget_inputs(self, context):
        names = context.backend_output["names"]
        if isinstance(names, str):
            names = [names]

        return {
            get_number_by_reciver_name_ui: WidgetInput(
                widget=Widget(
                    name="search_contacts_widget",
                    type="search_contacts_widget",
                    order=2,
                    layout="vertical",
                    fields=["names"],
                    values=[{"names": names}],
                ),
                args={"receiver_name": names, "language": context.language},
            ),
        }


get_number_by_receiver_name = GetNumberByReceiverName()


class GetReceiverIdByReceiverPhoneNumber(FunctionStrategy):
    """Strategy for phone number card selection UI."""

    def build_widget_inputs(self, context):
        backend_data = CardsByPhoneNumberResponse(**context.backend_output)
        return {
            get_receiver_id_by_receiver_phone_number_ui: WidgetInput(
                widget=Widget(
                    name="get_contacts_widget",
                    type="get_contacts_widget",
                    order=2,
                    layout="vertical",
                    fields=["receiver_name"],
                    values=[x.model_dump() for x in backend_data.cards],
                ),
                args={"cards": backend_data.cards, "language": context.language},
            ),
        }


get_receiver_id_by_receiver_phone_number = GetReceiverIdByReceiverPhoneNumber()


def get_receiver_id_by_receiver_phone_number_ui(
    cards: List[CardInfoByPhoneNumber],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Builds a UI showing a list of cards for a receiver using smarty_ui receiver_cards_list.

    Args:
        cards: List of card information
        language: Language for localization

    Returns:
        DivKit JSON for the card selection UI
    """
    # Convert CardInfoByPhoneNumber to receiver_cards_list format
    receiver_cards_data = []
    for card in cards:
        # Get provider logo URL based on processing system
        provider_logo = get_processing_system_icon(card.processing)

        receiver_cards_data.append(
            {
                "holder_name": card.name,
                "card_last_digits": card.mask[-4:] if card.mask else "****",
                "provider_logo_url": provider_logo,
                "action_url": f"divkit://select?card_id={card.pan}&card_name={card.name}&card_processing={card.processing}&card_mask={card.mask}",
            }
        )

    # Use smarty_ui receiver_cards_list component
    cards_widget = receiver_cards_list(receiver_cards_data)

    # Wrap with margins
    container = VStack([cards_widget])
    container.margins = dv.DivEdgeInsets(left=12, right=12, top=12, bottom=12)

    div = dv.make_div(container)
    with open(
        "logs/json/build_get_receiver_id_by_receiver_phone_number_ui.json", "w"
    ) as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


# ============================================================================
# Transaction Status UI using smarty_ui
# ============================================================================


def build_transfer_success_ui(
    amount: str,
    recipient: str,
    card_last_digits: str,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build transfer success UI using smarty_ui transaction_success_widget.

    Args:
        amount: Transfer amount
        recipient: Recipient name and card info
        card_last_digits: Last 4 digits of the card
        language: Language for localization

    Returns:
        DivKit JSON for the transfer success UI
    """
    feedback_texts = TRANSFER_FEEDBACK_TEXTS.get(
        language, TRANSFER_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    date_time = datetime.now().strftime("%-d %B %Y %H:%M")

    # Use smarty_ui transaction_success_widget
    success_widget = transaction_success_widget(
        amount=amount,
        recipient=f"{recipient} **{card_last_digits}",
        date_time=date_time,
        currency=feedback_texts["currency"],
    )

    # Wrap with margins
    container = VStack([success_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_transfer_success_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def build_transfer_failed_ui(
    amount: str,
    recipient: str,
    card_last_digits: str,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build transfer failed UI using smarty_ui transaction_failed_widget.

    Args:
        amount: Transfer amount
        recipient: Recipient name and card info
        card_last_digits: Last 4 digits of the card
        language: Language for localization

    Returns:
        DivKit JSON for the transfer failed UI
    """
    feedback_texts = TRANSFER_FEEDBACK_TEXTS.get(
        language, TRANSFER_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    date_time = datetime.now().strftime("%-d %B %Y %H:%M")

    # Use smarty_ui transaction_failed_widget
    failed_widget = transaction_failed_widget(
        amount=amount,
        recipient=f"{recipient} **{card_last_digits}",
        date_time=date_time,
        currency=feedback_texts["currency"],
    )

    # Wrap with margins
    container = VStack([failed_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_transfer_failed_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


# ============================================================================
# Cards Own List UI using smarty_ui
# ============================================================================


def build_cards_own_list_ui(
    cards_data: List[Dict[str, Any]],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build user's own cards list UI using smarty_ui cards_own_list component.

    Args:
        cards_data: List of card dicts with balance, card_name, card_thumbnail_url, card_last_digits
        language: Language for localization

    Returns:
        DivKit JSON for the cards list UI
    """
    # Use smarty_ui cards_own_list component
    cards_widget = cards_own_list(cards=cards_data)

    # Wrap with margins
    container = VStack([cards_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_cards_own_list_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


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
