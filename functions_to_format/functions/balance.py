import pydivkit as dv
from pydivkit.core import Expr
import json
from .general import (
    Widget,
    WidgetInput,
)
from pydantic import BaseModel
from typing import Any, List, Optional
from conf import logger
from models.context import Context
from .base_strategy import FunctionStrategy
from tool_call_models.cards import CardsBalanceResponse
from tool_call_models.home_balance import HomeBalance
from functions_to_format.functions.general.const_values import LanguageOptions

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    title_2,
    text_1,
    text_2,
    caption_1,
    icon,
    avatar,
    divider,
    simple_card,
    default_theme,
)

# Import smarty_ui blocks for ready-made components
from smarty_ui.blocks import (
    cards_own_list as smarty_cards_own_list,
    home_balance_widget as smarty_home_balance_widget,
)


# Feedback texts for balance actions
BALANCE_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "topup_success": "Пополнение выполнено",
        "transfer_success": "Перевод выполнен",
        "action_error": "Ошибка операции",
    },
    LanguageOptions.ENGLISH: {
        "topup_success": "Top up completed",
        "transfer_success": "Transfer completed",
        "action_error": "Operation failed",
    },
    LanguageOptions.UZBEK: {
        "topup_success": "To'ldirish bajarildi",
        "transfer_success": "O'tkazma bajarildi",
        "action_error": "Amal xatosi",
    },
}


class CardInfo(BaseModel):
    masked_card_pan: str
    image_url: str
    card_type: str
    balance: int
    card_name: str
    cardColor: str


class Account(BaseModel):
    """
    Pydantic model for account data.
    """

    image_url: str
    balance: str
    type: str


class BalanceInput(BaseModel):
    """
    Pydantic model for balance input containing cards and accounts.
    """

    cards: list[CardInfo] = []
    accounts: list[Account] = []


def format_balance(balance: int):
    """
    Format balance to include commas as thousand separators.

    Args:
        balance (int): The balance amount to format

    Returns:
        str: Formatted balance with commas (e.g. 100,000)
    """
    return f"{balance:,}"


def build_home_balances_ui_widget(
    home_balance: HomeBalance,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build home balances UI using smarty_ui home_balance_widget block component.
    """
    div = build_home_balances_ui(home_balance)
    output = dv.make_div(div)

    return output


def build_home_balances_ui(home_balance: HomeBalance | dict[str, Any]):
    """
    Build home balances UI using smarty_ui home_balance_widget block component.
    Creates a card with house icon and utility service options.
    """
    # Map service names to utility types for smarty_ui
    service_type_map = {
        "electricity": "electricity",
        "gas": "gas",
        "water": "water",
        "coldWater": "water",
        "hotWater": "water",
        "garbage": "recycling",
        "internet": "other",
        "mobile": "other",
        "heating": "other",
    }

    if isinstance(home_balance, dict):
        home_balance = HomeBalance(**home_balance)

    # Convert home_balance services to smarty_ui UtilityBalanceData format
    utilities = []
    for service_name, service_data in home_balance.services.items():
        utility_type = service_type_map.get(service_name, "other")
        balance_value = service_data.balance * 100  # Convert to minor units
        is_negative = balance_value < 0

        utilities.append(
            {
                "utility_type": utility_type,
                "balance": format_balance(abs(balance_value)),
                "currency": "сум",
                "is_negative": is_negative,
            }
        )

    # Use smarty_ui home_balance_widget block component
    home_widget = smarty_home_balance_widget(
        title=home_balance.homeName if home_balance.homeName else "Мой дом",
        subtitle="Балансы",
        utilities=utilities,
        corner_radius=20,
    )

    # Wrap with margins
    container = VStack([home_widget])
    container.margins = dv.DivEdgeInsets(left=15)

    return container


class GetHomeBalances(FunctionStrategy):
    """Strategy for building home balances UI."""

    def build_widget_inputs(self, context):
        backend_output = context.backend_output
        if "services" in backend_output:
            for k, v in backend_output["services"].items():
                backend_output[k] = v
            del backend_output["services"]

        backend_data = HomeBalance(**backend_output)
        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            text_builder: text_input,
            build_home_balances_ui_widget: WidgetInput(
                widget=Widget(
                    name="home_balance_widget",
                    type="home_balance_widget",
                    order=2,
                    layout="vertical",
                    fields=["homeName", "services"],
                    values=[backend_data.model_dump(exclude_none=True)],
                ),
                args={"home_balance": backend_data},
            ),
        }


get_home_balances = GetHomeBalances()


class GetBalance(FunctionStrategy):
    """Strategy for building balance UI."""

    def build_widget_inputs(self, context):
        logger = context.logger_context.logger
        logger.info(
            f"Processing balance request for chat_id: {context.logger_context.chat_id}"
        )

        backend_data = CardsBalanceResponse(**context.backend_output)
        logger.info(
            f"Successfully parsed backend data with {len(backend_data.body[0].cardList)} cards"
        )

        backend_output_processed = []
        for i, card_info in enumerate(backend_data.body[0].cardList):
            balance_value = 0
            if type(card_info.cardBalance.balance) is int:
                balance_value = card_info.cardBalance.balance
            elif type(card_info.cardBalance.balance) is str:
                balance_value = int(card_info.cardBalance.balance.replace(" ", ""))
            elif type(card_info.cardBalance.balance) is float:
                balance_value = int(card_info.cardBalance.balance)

            backend_output_processed.append(
                CardInfo(
                    masked_card_pan=card_info.pan,
                    card_type=card_info.processingSystem,
                    balance=balance_value,
                    card_name=card_info.cardDetails.cardName,
                    cardColor=card_info.cardDetails.cardColor,
                    image_url=card_info.bankIcon.bankLogoMini,
                )
            )

        logger.info(f"Processed {len(backend_output_processed)} cards successfully")

        text_builder, text_input = self.make_text_input(context.llm_output)
        return {
            text_builder: text_input,
            build_balance_ui_widget: WidgetInput(
                widget=Widget(
                    name="cards_own_list_widget_balance",
                    type="cards_own_list_widget_balance",
                    order=2,
                    layout="vertical",
                    fields=["masked_card_pan", "card_type", "balance", "card_name"],
                    values=[
                        card.model_dump(exclude_none=True)
                        for card in backend_output_processed
                    ],
                ),
                args={
                    "balance_input": BalanceInput(
                        cards=backend_output_processed, accounts=[]
                    ),
                    "language": context.language,
                },
            ),
        }


get_balance = GetBalance()


def card_block(card: CardInfo, language: LanguageOptions = LanguageOptions.RUSSIAN):
    """
    Create a UI container for displaying card information using smarty_ui.

    Args:
        card (dict): Card data including image_url, balance, last_digits, and type

    Returns:
        dv.DivContainer: UI component for card display
    """
    texts_map = {
        LanguageOptions.RUSSIAN: {
            "sum": "сум",
        },
        LanguageOptions.ENGLISH: {
            "sum": "sum",
        },
        LanguageOptions.UZBEK: {
            "sum": "so'm",
        },
    }
    sum_text = texts_map[language]["sum"]

    # Card image using smarty_ui icon
    card_image = dv.DivImage(
        image_url=card.image_url,
        width=dv.DivFixedSize(value=48),
        height=dv.DivFixedSize(value=32),
        scale=dv.DivImageScale.FIT,
    )

    # Balance text using text_1 (bold)
    balance_text = text_1(f"{card.balance // 100} {sum_text}", color="#111827")
    balance_text.font_weight = dv.DivFontWeight.BOLD

    # Card details using text_2
    card_details = text_2(
        f"💳 •• {card.masked_card_pan} — {card.card_type}",
        color="#6B7280",
    )

    # Card info column using VStack
    card_info = VStack([balance_text, card_details])

    # Main row using HStack
    card_row = HStack(
        [card_image, card_info],
        gap=12,
        align_v="center",
    )
    card_row.margins = dv.DivEdgeInsets(bottom=12)

    return card_row


def account_block(
    account: Account, language: LanguageOptions = LanguageOptions.RUSSIAN
):
    """
    Create a UI container for displaying account information using smarty_ui.

    Args:
        account (dict): Account data including image_url, balance, and type

    Returns:
        dv.DivContainer: UI component for account display
    """
    texts_map = {
        LanguageOptions.RUSSIAN: {
            "sum": "сум",
        },
        LanguageOptions.ENGLISH: {
            "sum": "sum",
        },
        LanguageOptions.UZBEK: {
            "sum": "so'm",
        },
    }

    sum_text = texts_map[language]["sum"]

    # Account image
    account_image = dv.DivImage(
        image_url=account.image_url,
        width=dv.DivFixedSize(value=48),
        height=dv.DivFixedSize(value=32),
        scale=dv.DivImageScale.FIT,
    )

    # Balance text using text_1 (bold)
    balance_text = text_1(f"{account.balance} {sum_text}", color="#111827")
    balance_text.font_weight = dv.DivFontWeight.BOLD

    # Account type using text_2
    account_type_text = text_2(f"💼 {account.type}", color="#6B7280")

    # Account info column using VStack
    account_info = VStack([balance_text, account_type_text])

    # Main row using HStack
    account_row = HStack(
        [account_image, account_info],
        gap=12,
        align_v="center",
    )
    account_row.margins = dv.DivEdgeInsets(bottom=12)

    return account_row


def action_button(
    text: str,
    action_type: str = "default",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Create an action button UI component with success/error feedback.

    Args:
        text (str): Button text
        action_type (str): Type of action for payload
        language (LanguageOptions): Language for localization

    Returns:
        dv.DivText: UI component for action button with feedback handling
    """
    button_id = f"action-{text.lower().replace(' ', '_')}"

    return dv.DivText(
        text=text,
        text_color="#2563EB",
        height=dv.DivFixedSize(value=36),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        paddings=dv.DivEdgeInsets(top=8, bottom=8),
        border=dv.DivBorder(corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")),
        actions=[
            dv.DivAction(
                log_id=button_id,
                url=f"div-action://{text.lower().replace(' ', '_')}",
                payload={
                    "action": action_type,
                    "button_text": text,
                },
            ),
            # Success feedback action
            dv.DivAction(
                log_id=f"{button_id}-success",
                url="div-action://set_variable?name=balance_action_success&value=1",
            ),
        ],
    )


def build_balance_ui_widget(
    balance_input: BalanceInput,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build the balance UI using smarty_ui cards_own_list block component.
    """

    div = build_balance_ui(balance_input, language)
    output = dv.make_div(div)
    with open("logs/json/build_balance_ui.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


def build_balance_ui(
    balance_input: BalanceInput | dict[str, Any],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build the balance UI using smarty_ui cards_own_list block component.

    Args:
        balance_input (BalanceInput): Pydantic model containing cards and accounts data

    Returns:
        dict: Complete UI definition in DivKit format
    """

    if isinstance(balance_input, dict):
        balance_input = BalanceInput(**balance_input)

    logger.info("Build balance ui")
    cards = balance_input.cards
    texts_map = {
        LanguageOptions.RUSSIAN: {
            "cards_title": "Баланс ваших карт:",
            "accounts_title": "Баланс ваших счетов:",
            "text": "Вы можете пополнить счёт или перевести средства на другую карту.",
            "actions": ["Пополнить", "Перевести"],
            "currency": "сум",
        },
        LanguageOptions.ENGLISH: {
            "cards_title": "Your cards balance:",
            "accounts_title": "Your accounts balance:",
            "text": "You can top up your account or transfer money to another card.",
            "actions": ["Top up", "Transfer"],
            "currency": "sum",
        },
        LanguageOptions.UZBEK: {
            "cards_title": "Sizning kartalaringizning balansi:",
            "accounts_title": "Sizning hisoblaringizning balansi:",
            "text": "Siz hisobingizni to'ldirishingiz yoki boshqa kartaga pul o'tkazishingiz mumkin.",
            "actions": ["To'ldirish", "O'tkazish"],
            "currency": "so'm",
        },
    }

    cards_title = texts_map[language]["cards_title"]
    currency = texts_map[language]["currency"]

    if cards:
        # Convert CardInfo to smarty_ui CardBalanceData format
        smarty_cards = []
        for card in cards:
            smarty_cards.append(
                {
                    "balance": format_balance(card.balance // 100),
                    "card_name": card.card_name,
                    "card_thumbnail_url": card,
                    "card_last_digits": card.masked_card_pan[-4:]
                    if len(card.masked_card_pan) >= 4
                    else card.masked_card_pan,
                    "currency": currency,
                }
            )

        # Use smarty_ui cards_own_list block component
        cards_widget = smarty_cards_own_list(
            cards=smarty_cards,
            corner_radius=8,
            padding=16,
        )

        # Add title above the cards widget
        title_text = caption_1(cards_title, color="#374151")
        title_text.font_weight = dv.DivFontWeight.BOLD
        title_text.margins = dv.DivEdgeInsets(bottom=8)

        root = VStack(
            [title_text, cards_widget],
            padding=0,
            width=dv.DivFixedSize(value=280),
        )
        root.margins = dv.DivEdgeInsets(top=16, left=20)
    else:
        # Empty state
        root = VStack(
            [],
            padding=16,
            background="#FFFFFF",
            corner_radius=8,
            width=dv.DivFixedSize(value=280),
        )
        root.margins = dv.DivEdgeInsets(top=16, left=20)

    return root


if __name__ == "__main__":
    cards = [
        {
            "image_url": "https://humocard.uz/bitrix/templates/main/img/card2.png",
            "balance": "1 200 000",
            "last_digits": "1234",
            "type": "VISA",
        },
        {
            "image_url": "https://humocard.uz/bitrix/templates/main/img/card2.png",
            "balance": "3 500 000",
            "last_digits": "5678",
            "type": "MasterCard",
        },
    ]

    accounts = [
        {
            "image_url": "https://humocard.uz/bitrix/templates/main/img/card2.png",
            "balance": "4 100 000",
            "type": "Депозит",
        }
    ]

    backend_output = {"cards": cards, "accounts": accounts}

    llm_output = json.dumps(
        {
            "text": "Вы можете пополнить счёт или перевести средства на другую карту.",
            "actions": ["Пополнить", "Перевести"],
        }
    )

    result = build_balance_ui(BalanceInput.model_validate(backend_output))

    with open("logs/json/jsons/balance_card.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
