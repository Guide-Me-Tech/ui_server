import pydivkit as dv
import json
from models.widget import Widget


class ButtonsWidget(Widget):
    name: str = "buttons_widget"
    type: str = "buttons_widget"
    layout: str = "horizontal"
    fields: list[str] = ["text", "action"]


def make_contacts_search_button(txt, receiver_name):
    if isinstance(receiver_name, list):
        search_contact_action = dv.DivAction(
            log_id="search_contact",
            url=f"divkit://search_contact?name={receiver_name}",  # Custom scheme the iOS app will catch
            payload={"name": receiver_name},  # Optional: structured access
        )
    else:
        search_contact_action = dv.DivAction(
            log_id="search_contact",
            url=f"divkit://search_contact?name=[{receiver_name}]",  # Custom scheme the iOS app will catch
            payload={"name": [receiver_name]},  # Optional: structured access
        )
    return dv.DivText(
        text="Qidirish",
        font_size=14,
        text_color="#2563EB",
        border=dv.DivBorder(corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")),
        alignment_horizontal="center",
        height=dv.DivFixedSize(value=36),
        paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
        margins=dv.DivEdgeInsets(right=8),
        action=search_contact_action,
    )


def build_buttons_row(button_texts: list, receiver_name: str = None):
    items = []
    for txt in button_texts:
        if txt == "search":
            items.append(make_contacts_search_button(txt, receiver_name))
        else:
            items.append(
                dv.DivText(
                    text=txt,
                    font_size=14,
                    text_color="#2563EB",
                    border=dv.DivBorder(
                        corner_radius=8, stroke=dv.DivStroke(color="#3B82F6")
                    ),
                    alignment_horizontal="center",
                    height=dv.DivFixedSize(value=36),
                    paddings=dv.DivEdgeInsets(left=12, right=12, top=8, bottom=8),
                    margins=dv.DivEdgeInsets(right=8),
                    action=dv.DivAction(
                        log_id=f"btn-{txt.lower()}",
                        url=f"divkit://button/{txt.lower()}",
                    ),
                )
            )

    div = dv.make_div(
        dv.DivContainer(
            orientation="horizontal",
            items=items,
            margins=dv.DivEdgeInsets(top=13, bottom=13),
        )
    )
    return div


if __name__ == "__main__":
    buttons = ["submit", "cancel"]
    buttons_widget = build_buttons_row(buttons)
    with open("temp/json/buttons.json", "w") as f:
        json.dump(buttons_widget, f)
