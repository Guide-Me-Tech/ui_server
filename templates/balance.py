import pydivkit as dv
import json


def card_block(card):
    return dv.DivContainer(
        orientation="horizontal",
        items=[
            dv.DivImage(
                image_url=card["image_url"],
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
                        text=f'{card["balance"]} сум',
                        font_size=16,
                        font_weight="bold",
                        text_color="#111827",
                    ),
                    dv.DivText(
                        text=f'💳 •• {card["last_digits"]} — {card["type"]}',
                        font_size=12,
                        text_color="#6B7280",
                    ),
                ],
            ),
        ],
        margins=dv.DivEdgeInsets(bottom=12),
    )


def account_block(account):
    return dv.DivContainer(
        orientation="horizontal",
        items=[
            dv.DivImage(
                image_url=account["image_url"],
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
                        text=f'{account["balance"]} сум',
                        font_size=16,
                        font_weight="bold",
                        text_color="#111827",
                    ),
                    dv.DivText(
                        text=f'💼 {account["type"]}', font_size=12, text_color="#6B7280"
                    ),
                ],
            ),
        ],
        margins=dv.DivEdgeInsets(bottom=12),
    )


def action_button(text):
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


# cards = [...]  # см. выше
# accounts = [...]  # см. выше

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

    with open("jsons/balance_card.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
