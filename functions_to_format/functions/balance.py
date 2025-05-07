import pydivkit as dv
import json
from .general import (
    add_ui_to_widget,
    Widget,
    WidgetInput,
    build_buttons_row,
    build_text_widget,
    TextWidget,
)
from pydantic import BaseModel
from typing import List
from conf import logger


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


def get_balance(llm_output, backend_output, version="v2"):
    """
    Process balance information and create UI widgets.

    Args:
        llm_output (str): Output from language model
        backend_output (dict): Card and account data from backend
        version (str, optional): UI version. Defaults to "v2".

    Returns:
        dict: Processed output with widgets
    """
    # Janis Rubins: use precompiled validator if available to avoid repeated validation overhead
    #  preprocess backend output:
    output = [
        llm_output,
    ]
    backend_output_processed: List[CardInfo] = []
    logger.info(f"backend_output {backend_output} ----- type:{type(backend_output)}")
    for i, card_info in enumerate(backend_output):
        backend_output_processed.append(
            CardInfo(
                masked_card_pan=card_info["pan"],
                card_type=card_info["processingSystem"],
                balance=(
                    card_info["balance"] if type(card_info["balance"]) is int else 0
                ),
                card_name=card_info["cardDetails"]["cardName"],
                cardColor=card_info["cardDetails"]["cardColor"],
                image_url=card_info["image_url"],
            )
        )
    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )
    cards_list = Widget(
        name="cards_own_list_widget_balance",
        type="cards_own_list_widget_balance",
        order=2,
        layout="vertical",
        fields=["masked_card_pan", "card_type", "balance", "card_name"],
        values=[card.model_dump() for card in backend_output_processed],
    )
    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
            build_balance_ui: WidgetInput(
                widget=cards_list,
                args={
                    "balance_input": BalanceInput(
                        cards=backend_output_processed, accounts=[]
                    ),
                },
            ),
        },
        version,
    )
    output = {"widgets": widgets, "widgets_count": 2}
    print("Output", output)

    return output


def card_block(card: CardInfo):
    """
    Create a UI container for displaying card information.

    Args:
        card (dict): Card data including image_url, balance, last_digits, and type

    Returns:
        dv.DivContainer: UI component for card display
    """
    return dv.DivContainer(
        orientation="horizontal",
        items=[
            dv.DivImage(
                image_url=card.image_url,
                width=dv.DivFixedSize(value=48),
                height=dv.DivFixedSize(value=32),
                scale=dv.DivImageScale.FIT,
                # corner_radius=6,
                margins=dv.DivEdgeInsets(right=12),
            ),
            dv.DivContainer(
                orientation="vertical",
                items=[
                    dv.DivText(
                        text=f"{card.balance} сум",
                        font_size=16,
                        font_weight="bold",
                        text_color="#111827",
                    ),
                    dv.DivText(
                        text=f"💳 •• {card.masked_card_pan} — {card.card_type}",
                        font_size=12,
                        text_color="#6B7280",
                    ),
                ],
            ),
        ],
        margins=dv.DivEdgeInsets(bottom=12),
    )


def account_block(account: Account):
    """
    Create a UI container for displaying account information.

    Args:
        account (dict): Account data including image_url, balance, and type

    Returns:
        dv.DivContainer: UI component for account display
    """
    return dv.DivContainer(
        orientation="horizontal",
        items=[
            dv.DivImage(
                image_url=account.image_url,
                width=dv.DivFixedSize(value=48),
                height=dv.DivFixedSize(value=32),
                scale=dv.DivImageScale.FIT,
                # corner_radius=6,
                margins=dv.DivEdgeInsets(right=12),
            ),
            dv.DivContainer(
                orientation="vertical",
                items=[
                    dv.DivText(
                        text=f"{account.balance} сум",
                        font_size=16,
                        font_weight="bold",
                        text_color="#111827",
                    ),
                    dv.DivText(
                        text=f"💼 {account.type}", font_size=12, text_color="#6B7280"
                    ),
                ],
            ),
        ],
        margins=dv.DivEdgeInsets(bottom=12),
    )


def action_button(text: str):
    """
    Create an action button UI component.

    Args:
        text (str): Button text

    Returns:
        dv.DivText: UI component for action button
    """
    return dv.DivText(
        text=text,
        text_color="#2563EB",
        height=dv.DivFixedSize(value=36),
        alignment_horizontal="center",
        paddings=dv.DivEdgeInsets(top=8, bottom=8),
        border=dv.DivBorder(corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")),
        action=dv.DivAction(
            log_id=f"action-{text.lower()}",
            url=f"div-action://{text.lower()}",  # или https://example.com/action
        ),
    )


def build_balance_ui(balance_input: BalanceInput):
    """
    Build the balance UI using backend data and LLM output.

    Args:
        balance_input (BalanceInput): Pydantic model containing cards and accounts data

    Returns:
        dict: Complete UI definition in DivKit format
    """
    # Convert backend_output to Pydantic models
    cards = balance_input.cards
    accounts = balance_input.accounts

    # Parse LLM output for text and actions
    text = "Вы можете пополнить счёт или перевести средства на другую карту."
    actions = ["Пополнить", "Перевести"]

    main_items = []

    if cards:
        main_items.append(
            dv.DivText(
                text="Баланс ваших карт:",
                font_size=13,
                font_weight="bold",
                text_color="#374151",
                margins=dv.DivEdgeInsets(bottom=8),
            )
        )
        main_items.extend([card_block(c) for c in cards])

    if accounts:
        main_items.append(
            dv.DivText(
                text="Баланс ваших счетов:",
                font_size=13,
                font_weight="bold",
                text_color="#374151",
                margins=dv.DivEdgeInsets(top=12, bottom=8),
            )
        )
        main_items.extend([account_block(a) for a in accounts])

    # Сообщение и кнопки
    main_items.append(
        dv.DivContainer(
            orientation="vertical",
            background=[dv.DivSolidBackground(color="#F9FAFB")],
            # border=dv.DivBorder(corner_radius=12),
            paddings=dv.DivEdgeInsets(top=16, bottom=16, left=16, right=16),
            items=[
                dv.DivText(text=text, font_size=13, text_color="#374151"),
                dv.DivContainer(
                    orientation="horizontal",
                    items=[action_button(act) for act in actions],
                    margins=dv.DivEdgeInsets(top=12),
                ),
            ],
            margins=dv.DivEdgeInsets(top=16),
        )
    )

    # Root контейнер
    root = dv.DivContainer(
        orientation="vertical",
        items=main_items,
        width=dv.DivMatchParentSize(),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        # border=dv.DivBorder(corner_radius=24),
        paddings=dv.DivEdgeInsets(top=16, bottom=16, left=16, right=16),
    )

    return dv.make_div(root)


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

    result = build_balance_ui(backend_output, llm_output)

    with open("jsons/balance_card.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)
