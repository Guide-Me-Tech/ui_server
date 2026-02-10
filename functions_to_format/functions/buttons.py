import pydivkit as dv
from pydivkit.core import Expr
import json
from typing import List, Optional

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    text_1,
    caption_1,
    default_theme,
)
from smarty_ui.primitives import smarty_button


# Feedback texts for button actions
BUTTON_FEEDBACK_TEXTS = {
    "ru": {
        "action_success": "Действие выполнено",
        "action_error": "Ошибка выполнения",
    },
    "en": {
        "action_success": "Action completed",
        "action_error": "Action failed",
    },
    "uz": {
        "action_success": "Amal bajarildi",
        "action_error": "Xatolik yuz berdi",
    },
}


def build_buttons_row(
    button_texts: list,
    language: str = "ru",
    include_feedback: bool = True,
):
    """
    Build a row of buttons with optional feedback handling using smarty_ui smarty_button component.

    Args:
        button_texts: List of button text labels
        language: Language code for feedback text (ru, en, uz)
        include_feedback: Whether to include success/error feedback containers

    Returns:
        DivContainer with buttons and optional feedback
    """
    feedback_texts = BUTTON_FEEDBACK_TEXTS.get(language, BUTTON_FEEDBACK_TEXTS["en"])

    # Build button items using smarty_ui smarty_button
    button_items = []
    for txt in button_texts:
        # Create smarty_button with action_url for the main action
        action_url = f"div-action://button/{txt.lower().replace(' ', '_')}"
        btn = smarty_button(text=txt, action_url=action_url)

        # Add custom actions including feedback action
        btn.actions = [
            dv.DivAction(
                log_id=f"btn-{txt.lower().replace(' ', '_')}",
                url=action_url,
                payload={"button_text": txt, "action": txt.lower()},
            ),
            # Success feedback action
            dv.DivAction(
                log_id=f"btn-{txt.lower().replace(' ', '_')}-success",
                url="div-action://set_variable?name=simple_btn_success_visible&value=1",
            ),
        ]
        btn.margins = dv.DivEdgeInsets(right=8)
        button_items.append(btn)

    if not include_feedback:
        return HStack(button_items)

    # Success feedback container using smarty_ui
    success_icon = caption_1("✅")
    success_icon.margins = dv.DivEdgeInsets(right=8)

    success_text = caption_1(feedback_texts["action_success"], color="#065F46")
    success_text.font_weight = dv.DivFontWeight.MEDIUM
    success_text.width = dv.DivMatchParentSize(weight=1)

    dismiss_success = caption_1("✕", color="#065F46")
    dismiss_success.font_weight = dv.DivFontWeight.BOLD
    dismiss_success.paddings = dv.DivEdgeInsets(left=8)
    dismiss_success.actions = [
        dv.DivAction(
            log_id="dismiss-simple-btn-success",
            url="div-action://set_variable?name=simple_btn_success_visible&value=0",
        )
    ]

    success_container = HStack(
        [success_icon, success_text, dismiss_success],
        padding=8,
        background="#ECFDF5",
        corner_radius=8,
        width=dv.DivMatchParentSize(),
    )
    success_container.id = "simple-btn-success"
    success_container.visibility = Expr(
        "@{simple_btn_success_visible == 1 ? 'visible' : 'gone'}"
    )
    success_container.margins = dv.DivEdgeInsets(top=8)
    success_container.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#A7F3D0", width=1)
    )

    # Error feedback container using smarty_ui
    error_icon = caption_1("⚠️")
    error_icon.margins = dv.DivEdgeInsets(right=8)

    error_text = caption_1(feedback_texts["action_error"], color="#B91C1C")
    error_text.font_weight = dv.DivFontWeight.MEDIUM
    error_text.width = dv.DivMatchParentSize(weight=1)

    dismiss_error = caption_1("✕", color="#B91C1C")
    dismiss_error.font_weight = dv.DivFontWeight.BOLD
    dismiss_error.paddings = dv.DivEdgeInsets(left=8)
    dismiss_error.actions = [
        dv.DivAction(
            log_id="dismiss-simple-btn-error",
            url="div-action://set_variable?name=simple_btn_error_visible&value=0",
        )
    ]

    error_container = HStack(
        [error_icon, error_text, dismiss_error],
        padding=8,
        background="#FEF2F2",
        corner_radius=8,
        width=dv.DivMatchParentSize(),
    )
    error_container.id = "simple-btn-error"
    error_container.visibility = Expr(
        "@{simple_btn_error_visible == 1 ? 'visible' : 'gone'}"
    )
    error_container.margins = dv.DivEdgeInsets(top=8)
    error_container.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#FECACA", width=1)
    )

    # Buttons row using HStack
    buttons_row = HStack(button_items)

    # Main container using VStack
    main_container = VStack([buttons_row, success_container, error_container])
    main_container.variables = [
        dv.IntegerVariable(name="simple_btn_success_visible", value=0),
        dv.IntegerVariable(name="simple_btn_error_visible", value=0),
    ]

    return dv.make_div(main_container)


if __name__ == "__main__":
    buttons = ["submit", "cancel"]
    buttons_widget = build_buttons_row(buttons)
    with open("logs/json/buttons.json", "w") as f:
        json.dump(dv.make_div(buttons_widget), f, indent=2, ensure_ascii=False)
