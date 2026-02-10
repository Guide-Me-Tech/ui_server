import pydivkit as dv
from pydivkit.core import Expr
import json
from pydantic import BaseModel
from typing import List, Optional
from .general import Widget, WidgetInput
from .general.const_values import WidgetMargins, LanguageOptions
from models.context import Context, LoggerContext
from .base_strategy import FunctionStrategy

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    title_2,
    text_1,
    text_2,
    caption_1,
    avatar,
    default_theme,
)
# Import smarty_ui blocks for ready-made components
from smarty_ui.blocks import contacts_list as smarty_contacts_list


# Feedback texts for contact widget actions
CONTACT_WIDGET_FEEDBACK_TEXTS = {
    LanguageOptions.RUSSIAN: {
        "contact_opened": "Контакт открыт",
        "contact_selected": "Контакт выбран",
        "action_error": "Ошибка",
    },
    LanguageOptions.ENGLISH: {
        "contact_opened": "Contact opened",
        "contact_selected": "Contact selected",
        "action_error": "Error",
    },
    LanguageOptions.UZBEK: {
        "contact_opened": "Kontakt ochildi",
        "contact_selected": "Kontakt tanlandi",
        "action_error": "Xatolik",
    },
}


class GetContact(FunctionStrategy):
    """Strategy for building contact UI."""

    def build_widget_inputs(self, context):
        return {
            build_contact_widget: WidgetInput(
                widget=Widget(
                    name="contact_widget",
                    type="contact_widget",
                    order=1,
                    layout="horizontal",
                    fields=["name", "avatar_url", "subtitle"],
                ),
                args={
                    "backend_output": context.backend_output,
                    "llm_output": context.llm_output,
                    "context": context.logger_context,
                },
            ),
        }


get_contact = GetContact()


def contact_widget(
    name: str,
    avatar_url: str,
    subtitle: str,
    clickable: bool = False,
    contact_id: Optional[str] = None,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Create a contact widget with optional click handling and feedback using smarty_ui.

    Args:
        name: Contact name
        avatar_url: Contact avatar image URL
        subtitle: Contact subtitle/description
        clickable: Whether the contact is clickable
        contact_id: Optional contact identifier for action payload
        language: Language for localization

    Returns:
        DivContainer for the contact widget
    """
    feedback_texts = CONTACT_WIDGET_FEEDBACK_TEXTS.get(
        language, CONTACT_WIDGET_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    # Avatar using smarty_ui avatar component
    contact_avatar = avatar(avatar_url, size=40)

    # Name text using text_1
    name_text = text_1(name, color="#111827")
    name_text.font_weight = dv.DivFontWeight.MEDIUM
    name_text.width = dv.DivWrapContentSize()

    # Subtitle using text_2
    subtitle_text = text_2(subtitle, color="#6B7280")
    subtitle_text.width = dv.DivWrapContentSize()

    # Contact info column using VStack
    contact_info = VStack([name_text, subtitle_text])

    # Main row using HStack
    base_container = HStack(
        [contact_avatar, contact_info],
        gap=12,
        align_v="center",
        padding=12,
        background="#FFFFFF",
        corner_radius=12,
        width=dv.DivMatchParentSize(),
    )
    base_container.border = dv.DivBorder(
        corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")
    )
    base_container.margins = dv.DivEdgeInsets(
        bottom=WidgetMargins.BOTTOM.value,
        top=WidgetMargins.TOP.value,
        left=WidgetMargins.LEFT.value,
        right=WidgetMargins.RIGHT.value,
    )

    if clickable:
        safe_name = name.replace(" ", "_").replace("+", "")
        base_container.actions = [
            # Main contact action
            dv.DivAction(
                log_id=f"contact_select_{safe_name}",
                url=f"divkit://contact/select",
                payload={
                    "contact_name": name,
                    "contact_id": contact_id or safe_name,
                    "subtitle": subtitle,
                },
            ),
            # Success feedback action
            dv.DivAction(
                log_id=f"contact_select_{safe_name}_success",
                url="div-action://set_variable?name=contact_widget_success&value=1",
            ),
        ]

    return base_container


class Contact(BaseModel):
    name: str
    avatar_url: str
    subtitle: str


class ContactWidgetInput(BaseModel):
    name: str
    avatar_url: str
    subtitle: str


class ContactsListInput(BaseModel):
    contacts: List[Contact]
    title: str = "Contacts"


def build_contact_widget(backend_output: dict, llm_output: str, context: LoggerContext):
    # Parse input data
    contact_data = ContactWidgetInput(**backend_output)

    # Create the contact widget
    contact = contact_widget(
        name=contact_data.name,
        avatar_url=contact_data.avatar_url,
        subtitle=contact_data.subtitle,
    )

    # Return the widget as a JSON-serializable object
    return dv.make_div(contact)


def make_contacts_list(
    contacts_data: List[Contact],
    title: str = "Contacts",
    clickable: bool = False,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Create a contacts list container using smarty_ui contacts_list block component.

    Args:
        contacts_data: List of contact data objects
        title: List title
        clickable: Whether contacts are clickable
        language: Language for localization

    Returns:
        DivContainer for the contacts list
    """
    feedback_texts = CONTACT_WIDGET_FEEDBACK_TEXTS.get(
        language, CONTACT_WIDGET_FEEDBACK_TEXTS[LanguageOptions.ENGLISH]
    )

    # Convert Contact objects to ContactData format expected by smarty_ui
    smarty_contacts = []
    for idx, contact in enumerate(contacts_data):
        contact_data = {
            "name": contact.name,
            "phone": contact.subtitle,  # subtitle is used as phone in our model
        }
        if contact.avatar_url:
            contact_data["avatar_url"] = contact.avatar_url
        if clickable:
            # Add action URL for clickable contacts
            safe_name = contact.name.replace(" ", "_").replace("+", "")
            contact_data["action_url"] = f"divkit://contact/select?contact_id={idx}&name={safe_name}"
        smarty_contacts.append(contact_data)

    # Use smarty_ui contacts_list block component
    contacts_widget = smarty_contacts_list(
        contacts=smarty_contacts,
        show_index=True,
        corner_radius=16,
        padding=16,
    )

    if clickable:
        # Wrap with title and feedback containers
        title_text = title_2(title, color="#111827")
        title_text.margins = dv.DivEdgeInsets(bottom=12)

        # Success feedback container using HStack
        success_icon = text_1("✅")
        success_icon.margins = dv.DivEdgeInsets(right=8)

        success_text = caption_1(feedback_texts["contact_selected"], color="#065F46")
        success_text.width = dv.DivMatchParentSize(weight=1)

        dismiss_btn = text_1("✕", color="#065F46")
        dismiss_btn.font_weight = dv.DivFontWeight.BOLD
        dismiss_btn.paddings = dv.DivEdgeInsets(left=8)
        dismiss_btn.actions = [
            dv.DivAction(
                log_id="dismiss-contacts-list-success",
                url="div-action://set_variable?name=contact_widget_success&value=0",
            )
        ]

        success_container = HStack(
            [success_icon, success_text, dismiss_btn],
            align_v="center",
            align_h="center",
            padding_top=10,
            padding_bottom=10,
            padding_left=12,
            padding_right=12,
            background="#ECFDF5",
            corner_radius=10,
            width=dv.DivMatchParentSize(),
        )
        success_container.id = "contacts-list-success"
        success_container.visibility = Expr(
            "@{contact_widget_success == 1 ? 'visible' : 'gone'}"
        )
        success_container.border = dv.DivBorder(
            corner_radius=10, stroke=dv.DivStroke(color="#A7F3D0", width=1)
        )
        success_container.margins = dv.DivEdgeInsets(top=12)

        # Main container using VStack
        container = VStack(
            [title_text, contacts_widget, success_container],
            padding=16,
            background="#F9FAFB",
            corner_radius=16,
            width=dv.DivMatchParentSize(),
        )
        container.variables = [
            dv.IntegerVariable(name="contact_widget_success", value=0),
            dv.IntegerVariable(name="contact_widget_error", value=0),
        ]
        return container

    # Non-clickable: just wrap with title
    title_text = title_2(title, color="#111827")
    title_text.margins = dv.DivEdgeInsets(bottom=12)

    return VStack(
        [title_text, contacts_widget],
        padding=16,
        background="#F9FAFB",
        corner_radius=16,
        width=dv.DivMatchParentSize(),
    )


def build_contacts_list_widget(backend_output: dict, llm_output: str):
    # Parse input data
    input_data = ContactsListInput(**backend_output)

    # Create the contacts list widget
    contacts_list = make_contacts_list(
        contacts_data=input_data.contacts, title=input_data.title
    )

    # Return the widget as a JSON-serializable object
    return dv.make_div(contacts_list)


if __name__ == "__main__":
    name = "Aslon Khamidov"
    avatar_url = "https://encrypted-tbn1.gstatic.com/images?q=tbn:ANd9GcRo8jLMi-7Tv_6BwGJ6n-m10tDsTJwbEIDC4cfnPYjeMpN-RnB400RbNJxoDAIO93K7mb1qbVBYhh1KPSOoCd58_wMsQ3pV86hnWJK-xg"
    subtitle = "Hello world"
    # Создание и сохранение JSON
    root = contact_widget(name, avatar_url, subtitle)

    with open("logs/json/contact.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)

    # Create and save contacts list JSON
    contacts = [
        Contact(name="Aslon Khamidov", avatar_url=avatar_url, subtitle="Hello world"),
        Contact(name="John Doe", avatar_url=avatar_url, subtitle="Software Engineer"),
        Contact(name="Jane Smith", avatar_url=avatar_url, subtitle="Product Manager"),
    ]

    contacts_list = make_contacts_list(contacts, "My Contacts")

    with open("logs/json/contacts_list.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(contacts_list), f, indent=2, ensure_ascii=False)
