from .general import Widget, WidgetInput, TextWidget, add_ui_to_widget
from models.build import BuildOutput


def start_page_widget(llm_output: str, backend_output: dict, version: str = "v2"):
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

    return BuildOutput(
        widgets_count=len(widgets),
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


def build_start_page_widget(llm_output: str, backend_output: dict, version: str = "v2"):
    return ""
