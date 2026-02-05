import pydivkit as dv
from pydivkit.core import Expr
import json
from models.widget import Widget
from .const_values import WidgetMargins, WidgetPaddings, ButtonInRowMargins
from .const_values import LanguageOptions
from typing import Optional, List, Dict, Any


class ButtonsWidget(Widget):
    name: str = "buttons_widget"
    type: str = "buttons_widget"
    layout: str = "horizontal"
    fields: list[str] = ["text", "action"]


# Feedback texts for button actions
BUTTON_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "search_success": "Поиск выполнен",
        "action_success": "Действие выполнено",
        "action_error": "Ошибка выполнения",
        "cancel_success": "Отменено",
    },
    LanguageOptions.ENGLISH: {
        "search_success": "Search completed",
        "action_success": "Action completed",
        "action_error": "Action failed",
        "cancel_success": "Cancelled",
    },
    LanguageOptions.UZBEK: {
        "search_success": "Qidiruv bajarildi",
        "action_success": "Amal bajarildi",
        "action_error": "Xatolik yuz berdi",
        "cancel_success": "Bekor qilindi",
    },
}


def create_button_success_actions(
    log_id: str,
    prefix: str = "btn",
) -> List[dv.DivAction]:
    """Create success actions for button feedback."""
    return [
        dv.DivAction(
            log_id=f"{log_id}-success-show",
            url=f"div-action://set_variable?name={prefix}_success_visible&value=1",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-error",
            url=f"div-action://set_variable?name={prefix}_error_visible&value=0",
        ),
    ]


def create_button_error_actions(
    log_id: str,
    prefix: str = "btn",
) -> List[dv.DivAction]:
    """Create error actions for button feedback."""
    return [
        dv.DivAction(
            log_id=f"{log_id}-error-show",
            url=f"div-action://set_variable?name={prefix}_error_visible&value=1",
        ),
        dv.DivAction(
            log_id=f"{log_id}-hide-success",
            url=f"div-action://set_variable?name={prefix}_success_visible&value=0",
        ),
    ]


def make_contacts_search_button(
    txt: str,
    receiver_name,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """Create a search contacts button with feedback handling."""
    feedback_texts = BUTTON_FEEDBACK_TEXTS.get(
        language, BUTTON_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    if isinstance(receiver_name, list):
        search_payload = {"name": receiver_name}
        search_url = f"divkit://search_contact?name={receiver_name}"
    else:
        search_payload = {"name": [receiver_name]}
        search_url = f"divkit://search_contact?name=[{receiver_name}]"

    # Main search action
    search_contact_action = dv.DivAction(
        log_id="search_contact",
        url=search_url,
        payload=search_payload,
    )

    # Success feedback action (triggered after native handler)
    success_action = dv.DivAction(
        log_id="search_contact_success",
        url="div-action://set_variable?name=btn_search_success_visible&value=1",
    )

    return dv.DivText(
        text=txt,
        font_size=14,
        text_color="#2563EB",
        border=dv.DivBorder(corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        height=dv.DivFixedSize(value=36),
        paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
        margins=dv.DivEdgeInsets(
            right=ButtonInRowMargins.RIGHT.value,
            top=ButtonInRowMargins.TOP.value,
            bottom=ButtonInRowMargins.BOTTOM.value,
            left=ButtonInRowMargins.LEFT.value,
        ),
        actions=[search_contact_action, success_action],
    )


def build_buttons_row(
    button_texts: list,
    receiver_name: str | None = None,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Build a row of buttons with consistent styling and feedback handling.

    Args:
        button_texts: List of button identifiers (e.g., ['search', 'cancel'])
        receiver_name: Optional name for search contact functionality
        language: Language for button text localization

    Returns:
        DivKit JSON for the buttons row with feedback containers
    """
    items = []
    feedback_texts = BUTTON_FEEDBACK_TEXTS.get(
        language, BUTTON_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    texts_map = {
        LanguageOptions.RUSSIAN: {
            "search": "Поиск",
            "cancel": "Отмена",
            "confirm": "Подтвердить",
            "retry": "Повторить",
            "back": "Назад",
            "next": "Далее",
            "submit": "Отправить",
        },
        LanguageOptions.ENGLISH: {
            "search": "Search",
            "cancel": "Cancel",
            "confirm": "Confirm",
            "retry": "Retry",
            "back": "Back",
            "next": "Next",
            "submit": "Submit",
        },
        LanguageOptions.UZBEK: {
            "search": "Qidirish",
            "cancel": "Bekor qilish",
            "confirm": "Tasdiqlash",
            "retry": "Qayta urinish",
            "back": "Orqaga",
            "next": "Keyingi",
            "submit": "Yuborish",
        },
    }

    for txt in button_texts:
        button_text = texts_map[language].get(txt, txt)

        if txt == "search":
            items.append(
                make_contacts_search_button(button_text, receiver_name, language)
            )
        elif txt == "cancel":
            # Cancel button with feedback
            items.append(
                dv.DivText(
                    text=button_text,
                    font_size=14,
                    text_color="#6B7280",
                    border=dv.DivBorder(
                        corner_radius=8, stroke=dv.DivStroke(color="#D1D5DB")
                    ),
                    alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    height=dv.DivFixedSize(value=36),
                    paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                    margins=dv.DivEdgeInsets(
                        right=ButtonInRowMargins.RIGHT.value,
                        top=ButtonInRowMargins.TOP.value,
                        bottom=ButtonInRowMargins.BOTTOM.value,
                        left=ButtonInRowMargins.LEFT.value,
                    ),
                    actions=[
                        dv.DivAction(
                            log_id=f"btn-cancel",
                            url=f"divkit://button/cancel",
                            payload={"action": "cancel"},
                        ),
                        dv.DivAction(
                            log_id="btn-cancel-feedback",
                            url="div-action://set_variable?name=btn_action_completed&value=1",
                        ),
                    ],
                )
            )
        else:
            # Standard button with feedback
            items.append(
                dv.DivText(
                    text=button_text,
                    font_size=14,
                    text_color="#2563EB",
                    border=dv.DivBorder(
                        corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                    ),
                    alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
                    height=dv.DivFixedSize(value=36),
                    paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                    margins=dv.DivEdgeInsets(
                        right=ButtonInRowMargins.RIGHT.value,
                        top=ButtonInRowMargins.TOP.value,
                        bottom=ButtonInRowMargins.BOTTOM.value,
                        left=ButtonInRowMargins.LEFT.value,
                    ),
                    actions=[
                        dv.DivAction(
                            log_id=f"btn-{txt.lower()}",
                            url=f"divkit://button/{txt.lower()}",
                            payload={"action": txt.lower()},
                        ),
                        dv.DivAction(
                            log_id=f"btn-{txt.lower()}-success",
                            url="div-action://set_variable?name=btn_success_visible&value=1",
                        ),
                    ],
                )
            )

    # Create success feedback container
    success_container = dv.DivContainer(
        id="btn-success-container",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{btn_success_visible == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=8, bottom=4),
        paddings=dv.DivEdgeInsets(top=8, bottom=8, left=12, right=12),
        background=[dv.DivSolidBackground(color="#ECFDF5")],
        border=dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        ),
        items=[
            dv.DivText(
                text="✅",
                font_size=13,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=feedback_texts["action_success"],
                font_size=13,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=14,
                text_color="#065F46",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-btn-success",
                        url="div-action://set_variable?name=btn_success_visible&value=0",
                    )
                ],
            ),
        ],
    )

    # Create error feedback container
    error_container = dv.DivContainer(
        id="btn-error-container",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{btn_error_visible == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=8, bottom=4),
        paddings=dv.DivEdgeInsets(top=8, bottom=8, left=12, right=12),
        background=[dv.DivSolidBackground(color="#FEF2F2")],
        border=dv.DivBorder(
            corner_radius=8, stroke=dv.DivStroke(color="#FECACA", width=1)
        ),
        items=[
            dv.DivText(
                text="⚠️",
                font_size=13,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=feedback_texts["action_error"],
                font_size=13,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=14,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-btn-error",
                        url="div-action://set_variable?name=btn_error_visible&value=0",
                    )
                ],
            ),
        ],
    )

    div = dv.make_div(
        dv.DivContainer(
            orientation=dv.DivContainerOrientation.VERTICAL,
            variables=[
                dv.IntegerVariable(name="btn_success_visible", value=0),
                dv.IntegerVariable(name="btn_error_visible", value=0),
                dv.IntegerVariable(name="btn_action_completed", value=0),
            ],
            items=[
                # Buttons row
                dv.DivContainer(
                    orientation=dv.DivContainerOrientation.HORIZONTAL,
                    items=items,
                ),
                # Feedback containers
                success_container,
                error_container,
            ],
            margins=dv.DivEdgeInsets(
                top=WidgetMargins.TOP.value,
                bottom=WidgetMargins.BOTTOM.value,
                left=WidgetMargins.LEFT.value,
                right=WidgetMargins.RIGHT.value,
            ),
        )
    )
    with open("logs/json/build_buttons.json", "w") as f:
        json.dump(div, f, indent=2, ensure_ascii=False)
    return div


if __name__ == "__main__":
    buttons = ["submit", "cancel"]
    buttons_widget = build_buttons_row(buttons)
    with open("logs/json/buttons.json", "w") as f:
        json.dump(buttons_widget, f)
