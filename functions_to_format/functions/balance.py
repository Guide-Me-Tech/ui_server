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
from models.build import BuildOutput
from tool_call_models.cards import CardsBalanceResponse
from tool_call_models.home_balance import HomeBalance


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


def build_balances_part(home_balance: HomeBalance):
    # Services list
    print(home_balance.services)
    service_icons = {
        "electricity": "https://smarty-test.smartbank.uz/ui_server/static/electricity.png",
        "gas": "https://smarty-test.smartbank.uz/ui_server/static/gas.png",
        "internet": "https://smarty-test.smartbank.uz/ui_server/static/trash.png",
        "water": "https://smarty-test.smartbank.uz/ui_server/static/water.png",
        "mobile": "https://smarty-test.smartbank.uz/ui_server/static/mobile.png",
        "garbage": "https://smarty-test.smartbank.uz/ui_server/static/trash.png",
        "coldWater": "https://smarty-test.smartbank.uz/ui_server/static/water.png",
        "hotWater": "https://smarty-test.smartbank.uz/ui_server/static/water.png",
        "heating": "https://smarty-test.smartbank.uz/ui_server/static/heating.png",
    }

    items = []
    for service_name, icon_url in service_icons.items():
        if service_name not in home_balance.services:
            continue
        try:
            items.append(
                dv.DivContainer(
                    orientation="horizontal",
                    width=dv.DivFixedSize(value=150)
                    if service_name == "electricity"
                    else None,
                    height=dv.DivFixedSize(value=24),
                    items=[
                        dv.DivImage(
                            image_url=icon_url,
                            width=dv.DivFixedSize(value=24),
                            height=dv.DivFixedSize(value=24),
                        ),
                        dv.DivText(
                            text=format_balance(
                                home_balance.services[service_name].balance
                            ),
                            font_size=16,
                            text_color="#666666",
                            margins=dv.DivEdgeInsets(
                                left=8 if service_name == "electricity" else 12
                            ),
                        ),
                    ],
                )
            )
        except KeyError:
            pass
        # Add separator after each service except the last one
        if service_name != "internet":
            items.append(
                dv.DivContainer(
                    height=dv.DivFixedSize(value=1),
                    background=[dv.DivSolidBackground(color="#E5E5E5")],
                    margins=dv.DivEdgeInsets(bottom=4, top=4),
                )
            )

    return dv.DivContainer(
        orientation="vertical",
        margins=dv.DivEdgeInsets(top=8),
        items=items,
    )


def build_home_balance_main_container(home_balance: HomeBalance):
    return dv.DivContainer(
        orientation="horizontal",
        width=dv.DivFixedSize(value=361),
        height=dv.DivFixedSize(value=150),
        background=[dv.DivSolidBackground(color="#EBF2FA")],
        border=dv.DivBorder(corner_radius=20),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=12, bottom=12),
        margins=dv.DivEdgeInsets(left=15),  # Added left margin to move card right
        items=[
            dv.DivContainer(
                orientation="vertical",
                items=[
                    dv.DivText(
                        text="Мой дом",
                        font_size=20,
                        font_weight="medium",
                        text_color="#000000",
                        margins=dv.DivEdgeInsets(bottom=8),
                    ),
                    dv.DivImage(
                        image_url="https://smarty-test.smartbank.uz/ui_server/static/home.png",
                        width=dv.DivFixedSize(value=60),
                        height=dv.DivFixedSize(value=60),
                    ),
                ],
            ),
            dv.DivContainer(
                orientation="vertical",
                margins=dv.DivEdgeInsets(left=64),
                items=[
                    build_balances_part(home_balance),
                ],
            ),
        ],
    )


def build_home_balances_ui(home_balance: HomeBalance):
    """
    Build home balances UI using Yandex DivKit SDK.
    Creates a card with house icon and utility service options.
    """
    container = build_home_balance_main_container(home_balance)
    output = dv.make_div(container)
    with open("build_home_balances_ui.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)
    return output


def get_home_balances(llm_output, backend_output, version="v2"):
    """
    Get home balances.
    """
    for k, v in backend_output["services"].items():
        backend_output[k] = v
    del backend_output["services"]

    backend_output: HomeBalance = HomeBalance(**backend_output)

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )
    home_Balance_Widget = Widget(
        name="home_balance_widget",
        type="home_balance_widget",
        order=2,
        layout="vertical",
        fields=["homeName", "services"],
        values=[backend_output.model_dump(exclude_none=True)],
    )

    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
            build_home_balances_ui: WidgetInput(
                widget=home_Balance_Widget,
                args={"home_balance": backend_output},
            ),
        },
        version,
    )
    output = BuildOutput(
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
        widgets_count=len(widgets),
    )
    return output


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
    backend_output: CardsBalanceResponse = CardsBalanceResponse(**backend_output)
    backend_output_processed: List[CardInfo] = []
    # logger.info(f"backend_output {backend_output} ----- type:{type(backend_output)}")
    for i, card_info in enumerate(backend_output.body[0].cardList):
        backend_output_processed.append(
            CardInfo(
                masked_card_pan=card_info.pan,
                card_type=card_info.processingSystem,
                balance=(
                    card_info.cardBalance.balance
                    if type(card_info.cardBalance.balance) is int
                    else 0
                ),
                card_name=card_info.cardDetails.cardName,
                cardColor=card_info.cardDetails.cardColor,
                image_url=card_info.bankIcon.bankLogoMini,
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
        values=[
            card.model_dump(exclude_none=True) for card in backend_output_processed
        ],
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
    output = BuildOutput(
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
        widgets_count=len(widgets),
    )
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
    logger.info("Build balance ui")
    cards = balance_input.cards

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

    # Сообщение и кнопки
    main_items.append(
        dv.DivContainer(
            orientation="vertical",
            background=[dv.DivSolidBackground(color="#F9FAFB")],
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
        width=dv.DivFixedSize(value=280),
        height=dv.DivFixedSize(value=248),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#E5E7EB", width=1)
        ),
        paddings=dv.DivEdgeInsets(top=16, bottom=16, left=16, right=16),
        margins=dv.DivEdgeInsets(top=16, left=20),
    )

    output = dv.make_div(root)
    with open("build_balance_ui.json", "w", encoding="utf-8") as f:
        json.dump(output, f, indent=2, ensure_ascii=False)

    return output


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
