import pydivkit as dv
from pydivkit.core import Expr
import json
from pydantic import BaseModel
from typing import List, Optional
from .general import Widget, add_ui_to_widget
from .general.utils import save_builder_output
from models.build import BuildOutput
from .general.const_values import WidgetMargins, LanguageOptions
from .general import WidgetInput
from conf import logger
import structlog

from models.context import Context, LoggerContext


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


def get_contact(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    widget = Widget(
        name="contact_widget",
        type="contact_widget",
        order=1,
        layout="horizontal",
        fields=["name", "avatar_url", "subtitle"],
    )
    widgets = add_ui_to_widget(
        {
            build_contact_widget: WidgetInput(
                widget=widget,
                args={
                    "backend_output": backend_output,
                    "llm_output": llm_output,
                    "context": context.logger_context,
                },
            )
        },
        version,
    )
    output = BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def contact_widget(
    name: str,
    avatar_url: str,
    subtitle: str,
    clickable: bool = False,
    contact_id: Optional[str] = None,
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    """
    Create a contact widget with optional click handling and feedback.
    
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
    feedback_texts = CONTACT_WIDGET_FEEDBACK_TEXTS.get(language, CONTACT_WIDGET_FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    
    base_container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.HORIZONTAL,
        items=[
            dv.DivImage(
                image_url=avatar_url,
                width=dv.DivFixedSize(value=40),
                height=dv.DivFixedSize(value=40),
                scale=dv.DivImageScale.FILL,
                margins=dv.DivEdgeInsets(right=12),
                border=dv.DivBorder(corner_radius=20),
            ),
            dv.DivContainer(
                orientation=dv.DivContainerOrientation.VERTICAL,
                items=[
                    dv.DivText(
                        text=name,
                        font_size=14,
                        font_weight=dv.DivFontWeight.MEDIUM,
                        text_color="#111827",
                    ),
                    dv.DivText(text=subtitle, font_size=12, text_color="#6B7280"),
                ],
            ),
        ],
        paddings=dv.DivEdgeInsets(top=12, bottom=12, right=12, left=12),
        background=[dv.DivSolidBackground(color="#FFFFFF")],
        border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")),
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(
            bottom=WidgetMargins.BOTTOM.value,
            top=WidgetMargins.TOP.value,
            left=WidgetMargins.LEFT.value,
            right=WidgetMargins.RIGHT.value,
        ),
    )
    
    if clickable:
        safe_name = name.replace(' ', '_').replace('+', '')
        base_container = dv.DivContainer(
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            items=[
                dv.DivImage(
                    image_url=avatar_url,
                    width=dv.DivFixedSize(value=40),
                    height=dv.DivFixedSize(value=40),
                    scale=dv.DivImageScale.FILL,
                    margins=dv.DivEdgeInsets(right=12),
                    border=dv.DivBorder(corner_radius=20),
                ),
                dv.DivContainer(
                    orientation=dv.DivContainerOrientation.VERTICAL,
                    items=[
                        dv.DivText(
                            text=name,
                            font_size=14,
                            font_weight=dv.DivFontWeight.MEDIUM,
                            text_color="#111827",
                        ),
                        dv.DivText(text=subtitle, font_size=12, text_color="#6B7280"),
                    ],
                ),
            ],
            paddings=dv.DivEdgeInsets(top=12, bottom=12, right=12, left=12),
            background=[dv.DivSolidBackground(color="#FFFFFF")],
            border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#E5E7EB")),
            width=dv.DivMatchParentSize(),
            margins=dv.DivEdgeInsets(
                bottom=WidgetMargins.BOTTOM.value,
                top=WidgetMargins.TOP.value,
                left=WidgetMargins.LEFT.value,
                right=WidgetMargins.RIGHT.value,
            ),
            actions=[
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
            ],
        )
    
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
    Create a contacts list container with optional click handling and feedback.
    
    Args:
        contacts_data: List of contact data objects
        title: List title
        clickable: Whether contacts are clickable
        language: Language for localization
        
    Returns:
        DivContainer for the contacts list
    """
    feedback_texts = CONTACT_WIDGET_FEEDBACK_TEXTS.get(language, CONTACT_WIDGET_FEEDBACK_TEXTS[LanguageOptions.ENGLISH])
    
    items: List[dv.Div] = [
        dv.DivText(
            text=title,
            font_size=16,
            font_weight=dv.DivFontWeight.BOLD,
            text_color="#111827",
            margins=dv.DivEdgeInsets(bottom=12),
        )
    ]

    for idx, contact in enumerate(contacts_data):
        items.append(
            contact_widget(
                name=contact.name,
                avatar_url=contact.avatar_url,
                subtitle=contact.subtitle,
                clickable=clickable,
                contact_id=str(idx),
                language=language,
            )
        )

    if clickable:
        # Success feedback container
        success_container = dv.DivContainer(
            id="contacts-list-success",
            orientation=dv.DivContainerOrientation.HORIZONTAL,
            visibility=Expr("@{contact_widget_success == 1 ? 'visible' : 'gone'}"),
            alignment_horizontal=dv.DivAlignmentHorizontal.CENTER,
            width=dv.DivMatchParentSize(),
            margins=dv.DivEdgeInsets(top=12),
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
                            log_id="dismiss-contacts-list-success",
                            url="div-action://set_variable?name=contact_widget_success&value=0",
                        )
                    ],
                ),
            ],
        )
        items.append(success_container)
        
        return dv.DivContainer(
            orientation=dv.DivContainerOrientation.VERTICAL,
            items=items,
            paddings=dv.DivEdgeInsets(all=16),
            background=[dv.DivSolidBackground(color="#F9FAFB")],
            border=dv.DivBorder(corner_radius=16),
            width=dv.DivMatchParentSize(),
            variables=[
                dv.IntegerVariable(name="contact_widget_success", value=0),
                dv.IntegerVariable(name="contact_widget_error", value=0),
            ],
        )

    return dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=items,
        paddings=dv.DivEdgeInsets(all=16),
        background=[dv.DivSolidBackground(color="#F9FAFB")],
        border=dv.DivBorder(corner_radius=16),
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
