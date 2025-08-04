import json
import re
import hashlib
from functools import lru_cache
from typing import Any, Dict, List
from conf import logger
from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    ButtonsWidget,
    build_buttons_row,
    build_text_widget,
    WidgetInput,
)
import pydivkit as dv
from models.build import BuildOutput
from pydantic import BaseModel
from .general.const_values import WidgetMargins

def chatbot_answer(llm_output: str, backend_output, version="v2") -> BuildOutput:
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data

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

    return BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


def unauthorized_response(llm_output, backend_output, version="v2"):
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data
    return {
        "data": llm_output,
    }


class Contact(BaseModel):
    first_name: str
    last_name: str
    phone: str


def build_contacts_list_widget(contacts: list[Contact]) -> Dict[str, Any]:
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

    for contact in contacts:
        send_action = dv.DivAction(
            log_id=f"send_contact_{contact.phone}",
            url="divkit://send_contact",
            payload={
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "phone": contact.phone,
            },
        )

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
            action=send_action,
        )
        items.append(contact_cell)

    container = dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=items,
        margins=dv.DivEdgeInsets(top=WidgetMargins.TOP.value, left=WidgetMargins.LEFT.value, right=WidgetMargins.RIGHT.value, bottom=WidgetMargins.BOTTOM.value),
        paddings=dv.DivEdgeInsets(left=16, right=16, top=8, bottom=8),
    )
    container = dv.make_div(container)
    with open("contacts.json", "w") as f:
        json.dump(container, f, indent=4)
    return container


def build_contacts_list(llm_output: str, backend_output: list[dict], version: str = "v2") -> BuildOutput:
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
                args={"button_texts": ["cancel"]},
            ),
            # build_text_widget: WidgetInput(
            #     widget=text_widget,
            #     args={"text": llm_output},
            # ),
        },
        version,
    )

    return BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
######### LEGACY UNUSED CODE #########