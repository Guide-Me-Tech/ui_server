import pydivkit as dv
from pydivkit.core import Expr
import json
from typing import List, Optional


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
    Build a row of buttons with optional feedback handling.
    
    Args:
        button_texts: List of button text labels
        language: Language code for feedback text (ru, en, uz)
        include_feedback: Whether to include success/error feedback containers
        
    Returns:
        DivContainer with buttons and optional feedback
    """
    feedback_texts = BUTTON_FEEDBACK_TEXTS.get(language, BUTTON_FEEDBACK_TEXTS["en"])
    
    button_items = [
        dv.DivText(
            text=txt,
            font_size=14,
            text_color="#2563EB",
            border=dv.DivBorder(
                corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
            ),
            alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
            height=dv.DivFixedSize(value=36),
            paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
            margins=dv.DivEdgeInsets(right=8),
            actions=[
                dv.DivAction(
                    log_id=f"btn-{txt.lower().replace(' ', '_')}",
                    url=f"div-action://button/{txt.lower().replace(' ', '_')}",
                    payload={"button_text": txt, "action": txt.lower()},
                ),
                # Success feedback action
                dv.DivAction(
                    log_id=f"btn-{txt.lower().replace(' ', '_')}-success",
                    url="div-action://set_variable?name=simple_btn_success_visible&value=1",
                ),
            ],
        )
        for txt in button_texts
    ]
    
    if not include_feedback:
        return dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            items=button_items,
        )
    
    # Success feedback container
    success_container = dv.DivContainer(
        id="simple-btn-success",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{simple_btn_success_visible == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=8),
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
                        log_id="dismiss-simple-btn-success",
                        url="div-action://set_variable?name=simple_btn_success_visible&value=0",
                    )
                ],
            ),
        ],
    )
    
    # Error feedback container
    error_container = dv.DivContainer(
        id="simple-btn-error",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{simple_btn_error_visible == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=8),
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
                        log_id="dismiss-simple-btn-error",
                        url="div-action://set_variable?name=simple_btn_error_visible&value=0",
                    )
                ],
            ),
        ],
    )
    
    return dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        variables=[
            dv.IntegerVariable(name="simple_btn_success_visible", value=0),
            dv.IntegerVariable(name="simple_btn_error_visible", value=0),
        ],
        items=[
            # Buttons row
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.HORIZONTAL,
                items=button_items,
            ),
            # Feedback containers
            success_container,
            error_container,
        ],
    )


if __name__ == "__main__":
    buttons = ["submit", "cancel"]
    buttons_widget = build_buttons_row(buttons)
    with open("logs/json/buttons.json", "w") as f:
        json.dump(dv.make_div(buttons_widget), f, indent=2, ensure_ascii=False)
