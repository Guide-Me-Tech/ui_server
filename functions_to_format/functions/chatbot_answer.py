import json
from typing import Any, Dict, List
from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    ButtonsWidget,
    build_buttons_row,
    build_text_widget,
    WidgetInput,
)
from .general.utils import save_builder_output
import pydivkit as dv
from pydivkit.core import Expr
from models.build import BuildOutput
from pydantic import BaseModel
from .general.const_values import WidgetMargins, LanguageOptions
from models.context import Context


# Feedback texts for contact actions
CONTACT_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "contact_selected": "Контакт выбран",
        "contact_error": "Ошибка выбора контакта",
    },
    LanguageOptions.ENGLISH: {
        "contact_selected": "Contact selected",
        "contact_error": "Contact selection error",
    },
    LanguageOptions.UZBEK: {
        "contact_selected": "Kontakt tanlandi",
        "contact_error": "Kontaktni tanlashda xatolik",
    },
}


def chatbot_answer(context: Context) -> BuildOutput:
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data

    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )

    output = BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def unauthorized_response(context: Context):
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    return {
        "data": llm_output,
    }


class Contact(BaseModel):
    first_name: str
    last_name: str
    phone: str


def build_contacts_list_widget(
    contacts: list[Contact],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build a contacts list widget with feedback handling for contact selection.

    Args:
        contacts: List of contact objects
        language: Language for localization

    Returns:
        DivKit JSON for the contacts list widget
    """
    feedback_texts = CONTACT_FEEDBACK_TEXTS.get(
        language, CONTACT_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    items: List[dv.Div] = [
        dv.DivText(
            text="Contacts List",
            font_family="Manrope",
            font_size=18,
            font_weight=dv.DivFontWeight.BOLD,
            text_color="#111133",
            margins=dv.DivEdgeInsets(bottom=16),
        )
    ]

    for idx, contact in enumerate(contacts):
        contact_cell = dv.DivContainer(
            orientation=dv.DivContainerOrientation.VERTICAL,
            paddings=dv.DivEdgeInsets(left=16, right=16, top=8, bottom=8),
            border=dv.DivBorder(
                stroke=dv.DivStroke(color="#E0E0E0"),
            ),
            items=[
                dv.DivText(
                    text=f"{contact.first_name} {contact.last_name}",
                    font_family="Manrope",
                    font_size=16,
                    font_weight=dv.DivFontWeight.MEDIUM,
                    text_color="#111133",
                    line_height=20,
                    letter_spacing=0,
                ),
                dv.DivText(
                    text=contact.phone,
                    font_family="Manrope",
                    font_size=14,
                    font_weight=dv.DivFontWeight.REGULAR,
                    text_color="#808080",
                    line_height=20,
                    letter_spacing=0,
                ),
            ],
            actions=[
                # Main selection action
                dv.DivAction(
                    log_id=f"send_contact_{contact.phone.replace('+', '').replace(' ', '')}",
                    url="divkit://send_contact",
                    payload={
                        "first_name": contact.first_name,
                        "last_name": contact.last_name,
                        "phone": contact.phone,
                    },
                ),
                # Success feedback action
                dv.DivAction(
                    log_id=f"send_contact_{idx}_success",
                    url="div-action://set_variable?name=contact_selection_success&value=1",
                ),
            ],
        )
        items.append(contact_cell)

    # Success feedback container
    success_container = dv.DivContainer(
        id="contact-selection-success",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{contact_selection_success == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, bottom=4),
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
                text=feedback_texts["contact_selected"],
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
                        log_id="dismiss-contact-selection-success",
                        url="div-action://set_variable?name=contact_selection_success&value=0",
                    )
                ],
            ),
        ],
    )

    # Error feedback container
    error_container = dv.DivContainer(
        id="contact-selection-error",
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        visibility=Expr("@{contact_selection_error == 1 ? 'visible' : 'gone'}"),
        alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(top=12, bottom=4),
        paddings=dv.DivEdgeInsets(top=10, bottom=10, left=12, right=12),
        background=[dv.DivSolidBackground(color="#FEF2F2")],
        border=dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#FECACA", width=1)
        ),
        items=[
            dv.DivText(
                text="⚠️",
                font_size=14,
                margins=dv.DivEdgeInsets(right=8),
            ),
            dv.DivText(
                text=feedback_texts["contact_error"],
                font_size=13,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.MEDIUM,
                width=dv.DivMatchParentSize(weight=1),
            ),
            dv.DivText(
                text="✕",
                font_size=16,
                text_color="#B91C1C",
                font_weight=dv.DivFontWeight.BOLD,
                paddings=dv.DivEdgeInsets(left=8),
                actions=[
                    dv.DivAction(
                        log_id="dismiss-contact-selection-error",
                        url="div-action://set_variable?name=contact_selection_error&value=0",
                    )
                ],
            ),
        ],
    )

    items.append(success_container)
    items.append(error_container)

    container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=items,
        variables=[
            dv.IntegerVariable(name="contact_selection_success", value=0),
            dv.IntegerVariable(name="contact_selection_error", value=0),
        ],
        margins=dv.DivEdgeInsets(
            top=WidgetMargins.TOP.value,
            left=WidgetMargins.LEFT.value,
            right=WidgetMargins.RIGHT.value,
            bottom=WidgetMargins.BOTTOM.value,
        ),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=8, bottom=8),
    )
    container = dv.make_div(container)
    with open("logs/json/build_contacts.json", "w") as f:
        json.dump(container, f, indent=4)
    return container


def build_contacts_list(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    contacts_list: list[Contact] = []

    contact_widget = Widget(
        order=1,
        name="contacts_list",
        type="contacts_list",
        layout="horizontal",
        fields=["contacts"],
        values=[{"contacts": contacts_list}],
    )
    # text_widget = TextWidget(
    #     order=1,
    #     values=[{"text": llm_output}],
    # )
    buttons = ButtonsWidget(
        order=2,
        values=[{"text": "cancel"}],
    )

    for contact in backend_output:
        contacts_list.append(
            Contact(
                first_name=contact["first_name"],
                last_name=contact["last_name"],
                phone=contact["phone"],
            )
        )

    widgets = add_ui_to_widget(
        {
            build_contacts_list_widget: WidgetInput(
                widget=contact_widget,
                args={
                    "contacts": contacts_list,
                },
            ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={"button_texts": ["cancel"], "language": language},
            ),
            # build_text_widget: WidgetInput(
            #     widget=text_widget,
            #     args={"text": llm_output},
            # ),
        },
        version,
    )

    output = BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output
