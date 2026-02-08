import json
from typing import Any, Dict, List

from smarty_ui.blocks import contacts_list
from .general import (
    Widget,
    ButtonsWidget,
    WidgetInput,
)
from .buttons import build_buttons_row
import pydivkit as dv
from pydivkit.core import Expr
from pydantic import BaseModel
from .general.const_values import WidgetMargins, LanguageOptions
from models.context import Context
from .base_strategy import FunctionStrategy

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    title_2,
    text_1,
    text_2,
    caption_1,
    caption_2,
    avatar,
    default_theme,
)
from smarty_ui.composites import user_bubble, assistant_bubble


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


class ChatbotAnswer(FunctionStrategy):
    """Strategy for chatbot answer - simple text widget."""

    def build_widget_inputs(self, context):
        text_builder, text_input = self.make_text_input(context.llm_output)
        return {text_builder: text_input}


chatbot_answer = ChatbotAnswer()


def unauthorized_response(context: Context):
    return {"data": context.llm_output}


class Contact(BaseModel):
    first_name: str
    last_name: str
    phone: str


# ============================================================================
# Contacts List UI using smarty_ui
# ============================================================================


def build_contacts_list_ui(
    contacts: List[Contact],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build contacts list UI using smarty_ui contacts_list component.

    Args:
        contacts_data: List of contact dicts with 'name' and 'phone' keys
        language: Language for localization

    Returns:
        DivKit JSON for the contacts list UI
    """
    # Use smarty_ui contacts_list component
    contacts_data = [
        {
            "name": f"{contact.first_name} {contact.last_name}",
            "phone": contact.phone,
            "action_url": f"divkit://send_contact?phone={contact.phone}",
            "avatar_url": f"https://ui-avatars.com/api/?name={contact.first_name}+{contact.last_name}",
        }
        for contact in contacts
    ]

    contacts_widget = contacts_list(contacts_data)

    # Wrap with margins
    container = VStack([contacts_widget])
    container.margins = dv.DivEdgeInsets(left=16, right=16, top=16, bottom=16)

    div = dv.make_div(container)
    with open("logs/json/build_contacts_list_ui.json", "w") as f:
        json.dump(div, f, ensure_ascii=False, indent=2)
    return div


def build_contacts_list_widget(
    contacts: list[Contact],
    language: LanguageOptions = LanguageOptions.RUSSIAN,
) -> Dict[str, Any]:
    """
    Build a contacts list widget using smarty_ui contacts_list component.

    Args:
        contacts: List of contact objects
        language: Language for localization

    Returns:
        DivKit JSON for the contacts list widget
    """
    # Convert contacts to the format expected by smarty_ui contacts_list
    contacts_data = [
        {
            "name": f"{contact.first_name} {contact.last_name}",
            "phone": contact.phone,
            "action_url": f"divkit://send_contact?phone={contact.phone}&first_name={contact.first_name}&last_name={contact.last_name}",
            "avatar_url": f"https://ui-avatars.com/api/?name={contact.first_name}+{contact.last_name}",
        }
        for contact in contacts
    ]

    # Use smarty_ui contacts_list component
    contacts_widget = contacts_list(
        contacts=contacts_data,
        show_index=True,
        corner_radius=8,
        padding=16,
        item_spacing=12,
    )

    # Wrap with margins
    container = VStack([contacts_widget])
    container.margins = dv.DivEdgeInsets(
        top=WidgetMargins.TOP.value,
        left=WidgetMargins.LEFT.value,
        right=WidgetMargins.RIGHT.value,
        bottom=WidgetMargins.BOTTOM.value,
    )

    result = dv.make_div(container)
    with open("logs/json/build_contacts.json", "w") as f:
        json.dump(result, f, indent=4)
    return result


class BuildContactsList(FunctionStrategy):
    """Strategy for building contacts list UI."""

    def build_widget_inputs(self, context):
        contacts_list = [
            Contact(
                first_name=c["first_name"],
                last_name=c["last_name"],
                phone=c["phone"],
            )
            for c in context.backend_output
        ]
        return {
            build_contacts_list_widget: WidgetInput(
                widget=Widget(
                    order=1,
                    name="contacts_list",
                    type="contacts_list",
                    layout="horizontal",
                    fields=["contacts"],
                    values=[{"contacts": contacts_list}],
                ),
                args={"contacts": contacts_list},
            ),
            build_buttons_row: WidgetInput(
                widget=ButtonsWidget(order=2, values=[{"text": "cancel"}]),
                args={"button_texts": ["cancel"], "language": context.language},
            ),
        }


build_contacts_list = BuildContactsList()
