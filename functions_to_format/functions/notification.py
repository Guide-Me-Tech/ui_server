import pydivkit as dv
import json
from pydantic import BaseModel
from typing import List
from .general import Widget, WidgetInput
from .base_strategy import FunctionStrategy
from models.context import Context, LoggerContext

# Import smarty_ui components
from smarty_ui import (
    VStack,
    HStack,
    text_1,
    text_2,
    caption_1,
    default_theme,
)


class GetNotifications(FunctionStrategy):
    """Strategy for building notifications UI."""

    def build_widget_inputs(self, context):
        notification_input = NotificationsInput(
            notifications=context.backend_output["notifications"]
        )
        return {
            build_notifications_widget: WidgetInput(
                widget=Widget(
                    name="notifications_widget",
                    type="notifications_widget",
                    layout="vertical",
                    order=1,
                    fields=["notifications"],
                ),
                args={
                    "notification_input": notification_input,
                    "context": context.logger_context,
                },
            ),
        }


get_notifications = GetNotifications()


def notification_widget(title, description):
    """Create a notification widget using smarty_ui components."""
    # Title using text_1 with bold weight
    title_text = text_1(title, color="#1E3A8A")
    title_text.font_weight = dv.DivFontWeight.BOLD

    # Description using text_2
    desc_text = text_2(description, color="#374151")
    desc_text.margins = dv.DivEdgeInsets(top=4)

    # Container using VStack
    container = VStack(
        [title_text, desc_text],
        padding=16,
        background="#EFF6FF",
        corner_radius=12,
        width=dv.DivMatchParentSize(),
    )
    container.border = dv.DivBorder(
        corner_radius=12, stroke=dv.DivStroke(color="#BFDBFE")
    )

    return container


class Notification(BaseModel):
    title: str
    description: str


class NotificationsInput(BaseModel):
    notifications: List[Notification]


def build_notifications_widget(
    notification_input: NotificationsInput,
    context: LoggerContext,
):
    """Build notifications widget using smarty_ui components."""
    # Create notification widgets
    notification_items = []
    for notification in notification_input.notifications:
        notification_items.append(
            notification_widget(
                title=notification.title, description=notification.description
            )
        )

    # Create container for all notifications using VStack
    notifications_container = VStack(
        notification_items,
        gap=8,
        width=dv.DivMatchParentSize(),
    )
    notifications_container.margins = dv.DivEdgeInsets(left=8, right=8, top=8, bottom=8)

    # Return the widget as a JSON-serializable object
    return dv.make_div(notifications_container)


if __name__ == "__main__":
    title = "Alert"
    description = "Fraudalent transaction"
    root = notification_widget(title, description)

    with open("logs/json/notification.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
