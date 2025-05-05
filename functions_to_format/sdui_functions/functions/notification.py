import pydivkit as dv
import json
from pydantic import BaseModel
from typing import List


def notification_widget(title, description):
    return dv.DivContainer(
        orientation="vertical",
        items=[
            dv.DivText(
                text=title, font_size=14, font_weight="bold", text_color="#1E3A8A"
            ),
            dv.DivText(
                text=description,
                font_size=13,
                text_color="#374151",
                margins=dv.DivEdgeInsets(top=4),
            ),
        ],
        paddings=dv.DivEdgeInsets(left=16, right=16, bottom=16, top=16),
        background=[dv.DivSolidBackground(color="#EFF6FF")],
        border=dv.DivBorder(corner_radius=12, stroke=dv.DivStroke(color="#BFDBFE")),
        width=dv.DivMatchParentSize(),
    )


class Notification(BaseModel):
    title: str
    description: str


class NotificationsInput(BaseModel):
    notifications: List[Notification]


def build_notifications_widget(backend_output: dict, llm_output: str):
    # Parse input data
    input_data = NotificationsInput(**backend_output)

    # Create notification widgets
    notification_items = []
    for notification in input_data.notifications:
        notification_items.append(
            notification_widget(
                title=notification.title, description=notification.description
            )
        )

    # Create container for all notifications
    notifications_container = dv.DivContainer(
        orientation="vertical",
        items=notification_items,
        width=dv.DivMatchParentSize(),
        margins=dv.DivEdgeInsets(all=8),
    )

    # Return the widget as a JSON-serializable object
    return dv.make_div(notifications_container)


if __name__ == "__main__":
    title = "Alert"
    description = "Fraudalent transaction"
    root = notification_widget(title, description)

    with open("jsons/notification.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
