from .general import Widget, WidgetInput
from .base_strategy import FunctionStrategy
from functions_to_format.functions.general.const_values import LanguageOptions
from models.context import Context


class StartPageWidget(FunctionStrategy):
    """Strategy for building start page UI."""
    def build_widget_inputs(self, context):
        return {
            build_start_page_widget: WidgetInput(
                widget=Widget(
                    name="start_page", type="start_page",
                    order=1, layout="vertical", fields=[],
                ),
                args={},
            ),
        }

start_page_widget = StartPageWidget()


def build_start_page_widget(
    llm_output: str,
    backend_output: dict,
    version: str = "v2",
    language: LanguageOptions = LanguageOptions.RUSSIAN,
):
    return ""
