import pydivkit as dv
import json
from pydantic import BaseModel
from typing import List
from .general import Widget, add_ui_to_widget, WidgetInput


def get_notifications(llm_output: str, backend_output: dict, version: str = "v3"):
    notifications_widget = Widget(
        name="notifications_widget",
        type="notifications_widget",
        layout="vertical",
        order=1,
        fields=["notifications"],
    )
    notification_input = NotificationsInput(
        notifications=backend_output["notifications"]
    )

    widgets = add_ui_to_widget(
        {
            build_notifications_widget: WidgetInput(
                widget=notifications_widget,
                args={
                    "notification_input": notification_input,
                },
            ),
        },
        version,
    )
    return {
        "widgets_count": 1,
        "widgets": [widget.model_dump(exclude_none=True) for widget in widgets],
    }


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


def build_notifications_widget(notification_input: NotificationsInput):
    # Parse input data

    # Create notification widgets
    notification_items = []
    for notification in notification_input.notifications:
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
        margins=dv.DivEdgeInsets(left=8, right=8, top=8, bottom=8),
    )

    # Return the widget as a JSON-serializable object
    return dv.make_div(notifications_container)


if __name__ == "__main__":
    title = "Alert"
    description = "Fraudalent transaction"
    root = notification_widget(title, description)

    with open("jsons/notification.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
