from .general import Widget, WidgetInput, TextWidget, add_ui_to_widget
from .general.utils import save_builder_output
from models.build import BuildOutput
from functions_to_format.functions.general.const_values import LanguageOptions
from conf import logger
import structlog
from models.context import Context


def start_page_widget(context: Context) -> BuildOutput:
    # Extract values from context
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version
    language = context.language
    chat_id = context.logger_context.chat_id
    api_key = context.api_key
    logger = context.logger_context.logger

    a = Widget(
        name="start_page",
        type="start_page",
        order=1,
        layout="vertical",
        fields=[],
    )
    widgets = add_ui_to_widget(
        widget_inputs={build_start_page_widget: WidgetInput(widget=a, args={})},
        version=version,
    )

    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )
    save_builder_output(context, output)
    return output


def build_start_page_widget(
    llm_output: str,
    backend_output: dict,
    version: str = "v2",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    return ""
