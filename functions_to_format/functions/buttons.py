import pydivkit as dv
from pydivkit.core import Expr
import json
import uuid
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
    include_feedback: bool = False,
):
    """
    Build a row of buttons with optional feedback handling using smarty_ui smarty_button component.

    Args:
        button_texts: List of button text labels
        language: Language code for feedback text (ru, en, uz)
        include_feedback: Whether to include success/error feedback containers (default: False)

    Returns:
        DivContainer with buttons and optional feedback
    """
    # Generate unique ID for this button row instance to avoid variable conflicts
    btn_row_uuid = str(uuid.uuid4())[:8]

    feedback_texts = BUTTON_FEEDBACK_TEXTS.get(language, BUTTON_FEEDBACK_TEXTS["en"])

    # Unique variable names for this button row instance
    success_var = f"btn_row_{btn_row_uuid}_success_visible"
    error_var = f"btn_row_{btn_row_uuid}_error_visible"

    # Build button items using smarty_ui smarty_button
    button_items = []
    for txt in button_texts:
        # Create smarty_button with action_url for the main action
        action_url = f"div-action://button/{txt.lower().replace(' ', '_')}"
        btn = smarty_button(text=txt, action_url=action_url)

        # Add custom actions (feedback action only if include_feedback is True)
        actions = [
            dv.DivAction(
                log_id=f"btn-{txt.lower().replace(' ', '_')}-{btn_row_uuid}",
                url=action_url,
                payload={"button_text": txt, "action": txt.lower()},
            ),
        ]

        if include_feedback:
            # Success feedback action
            actions.append(
                dv.DivAction(
                    log_id=f"btn-{txt.lower().replace(' ', '_')}-success-{btn_row_uuid}",
                    url=f"div-action://set_variable?name={success_var}&value=1",
                )
            )

        btn.actions = actions
        btn.margins = dv.DivEdgeInsets(right=8)
        button_items.append(btn)

    if not include_feedback:
        # Return simple HStack without feedback containers and without variables
        buttons_row = HStack(button_items)
        return dv.make_div(buttons_row)

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
            log_id=f"dismiss-btn-success-{btn_row_uuid}",
            url=f"div-action://set_variable?name={success_var}&value=0",
        )
    ]

    success_container = HStack(
        [success_icon, success_text, dismiss_success],
        padding=8,
        background="#ECFDF5",
        corner_radius=8,
        width=dv.DivMatchParentSize(),
    )
    success_container.id = f"btn-success-{btn_row_uuid}"
    success_container.visibility = Expr(
        f"@{{{success_var} == 1 ? 'visible' : 'gone'}}"
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
            log_id=f"dismiss-btn-error-{btn_row_uuid}",
            url=f"div-action://set_variable?name={error_var}&value=0",
        )
    ]

    error_container = HStack(
        [error_icon, error_text, dismiss_error],
        padding=8,
        background="#FEF2F2",
        corner_radius=8,
        width=dv.DivMatchParentSize(),
    )
    error_container.id = f"btn-error-{btn_row_uuid}"
    error_container.visibility = Expr(
        f"@{{{error_var} == 1 ? 'visible' : 'gone'}}"
    )
    error_container.margins = dv.DivEdgeInsets(top=8)
    error_container.border = dv.DivBorder(
        corner_radius=8, stroke=dv.DivStroke(color="#FECACA", width=1)
    )

    # Buttons row using HStack
    buttons_row = HStack(button_items)

    # Main container using VStack with scoped variables
    main_container = VStack([buttons_row, success_container, error_container])
    main_container.variables = [
        dv.IntegerVariable(name=success_var, value=0),
        dv.IntegerVariable(name=error_var, value=0),
    ]

    return dv.make_div(main_container)


if __name__ == "__main__":
    buttons = ["submit", "cancel"]
    # Test without feedback (default)
    buttons_widget = build_buttons_row(buttons)
    with open("logs/json/buttons.json", "w") as f:
        json.dump(buttons_widget, f, indent=2, ensure_ascii=False)

    # Test with feedback
    buttons_widget_with_feedback = build_buttons_row(buttons, include_feedback=True)
    with open("logs/json/buttons_with_feedback.json", "w") as f:
        json.dump(buttons_widget_with_feedback, f, indent=2, ensure_ascii=False)
