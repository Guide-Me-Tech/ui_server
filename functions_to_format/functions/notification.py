import pydivkit as dv
import json
from pydantic import BaseModel
from typing import List
from .general import Widget, add_ui_to_widget, WidgetInput
from .general.utils import save_builder_output
from models.build import BuildOutput
from functions_to_format.functions.general.const_values import LanguageOptions
from conf import logger
from models.context import Context, LoggerContext
import structlog


def get_notifications(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

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
                    "context": context.logger_context,
                },
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


def notification_widget(title, description):
    return dv.DivContainer(
        orientation=dv.DivContainerOrientation.VERTICAL,
        items=[
            dv.DivText(
                text=title,
                font_size=14,
                font_weight=dv.DivFontWeight.BOLD,
                text_color="#1E3A8A",
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


def build_notifications_widget(
    notification_input: NotificationsInput,
    context: LoggerContext,
):
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
        orientation=dv.DivContainerOrientation.VERTICAL,
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

    with open("logs/json/notification.json", "w", encoding="utf-8") as f:
        json.dump(dv.make_div(root), f, indent=2, ensure_ascii=False)
