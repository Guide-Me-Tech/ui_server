import pydivkit as dv
import json
from pydantic import BaseModel
from typing import List


def contact_widget(name, avatar_url, subtitle):
    return dv.DivContainer(
        orientation="horizontal",
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
                orientation="vertical",
                items=[
                    dv.DivText(
                        text=name,
                        font_size=14,
                        font_weight="medium",
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
        margins=dv.DivEdgeInsets(bottom=8),
    )


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


def build_contact_widget(backend_output: dict, llm_output: str):
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


def make_contacts_list(contacts_data: List[Contact], title: str = "Contacts"):
    items = [
        dv.DivText(
            text=title,
            font_size=16,
            font_weight="bold",
            text_color="#111827",
            margins=dv.DivEdgeInsets(bottom=12),
        )
    ]

    for contact in contacts_data:
        items.append(
            contact_widget(
                name=contact.name,
                avatar_url=contact.avatar_url,
                subtitle=contact.subtitle,
            )
        )

    return dv.DivContainer(
        orientation="vertical",
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

    with open("jsons/contact.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)

    # Create and save contacts list JSON
    contacts = [
        Contact(name="Aslon Khamidov", avatar_url=avatar_url, subtitle="Hello world"),
        Contact(name="John Doe", avatar_url=avatar_url, subtitle="Software Engineer"),
        Contact(name="Jane Smith", avatar_url=avatar_url, subtitle="Product Manager"),
    ]

    contacts_list = make_contacts_list(contacts, "My Contacts")

    with open("jsons/contacts_list.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(contacts_list), f, indent=2, ensure_ascii=False)
