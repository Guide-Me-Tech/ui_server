from .general import Widget, WidgetInput, TextWidget, add_ui_to_widget
from models.build import BuildOutput


def start_page_widget(llm_output: str, backend_output: dict, version: str = "v2"):
    a = Widget(
        id="start_page",
        type="start_page",
        data="",
    )
    widgets = add_ui_to_widget(
        widget_inputs={build_start_page_widget: WidgetInput(widget=a, args={})}
    )

    return BuildOutput(widgets_count=len(widgets), widgets=widgets)


def build_start_page_widget(llm_output: str, backend_output: dict, version: str = "v2"):
    return ""
