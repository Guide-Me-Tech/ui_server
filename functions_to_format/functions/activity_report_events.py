from .general import Widget, add_ui_to_widget, WidgetInput
from .general.utils import save_builder_output
from models.build import BuildOutput
from models.context import Context

from .activity_report import (
    FunctionCallBackendOutput,
    FunctionResponseBackendOutput,
    build_function_call_activity_widget,
    build_function_response_activity_widget,
)


def function_call_activity_record(context: Context) -> BuildOutput:
    """Build UI for function_call activity: message from llm_output, function_name + arguments from backend_output."""
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version

    data = FunctionCallBackendOutput(
        function_name=backend_output.get("function_name", ""),
        arguments=backend_output.get("arguments", {}),
    )

    activity_widget = Widget(
        name="function_call_activity_widget",
        type="function_call_activity_widget",
        order=1,
        layout="vertical",
        fields=["function_call_activity"],
    )
    inp = {
        build_function_call_activity_widget: WidgetInput(
            widget=activity_widget,
            args={
                "message": llm_output,
                "function_name": data.function_name,
                "arguments": data.arguments,
            },
        )
    }
    widgets = add_ui_to_widget(widget_inputs=inp, version=version)
    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[w.model_dump(exclude_none=True) for w in widgets],
    )
    save_builder_output(context, output)
    return output


def function_response_activity_record(context: Context) -> BuildOutput:
    """Build UI for function_response activity: message from llm_output, function_name + response from backend_output."""
    llm_output = context.llm_output
    backend_output = context.backend_output
    version = context.version

    data = FunctionResponseBackendOutput(
        function_name=backend_output.get("function_name", ""),
        response=backend_output.get("response", {}),
    )

    activity_widget = Widget(
        name="function_response_activity_widget",
        type="function_response_activity_widget",
        order=1,
        layout="vertical",
        fields=["function_response_activity"],
    )
    inp = {
        build_function_response_activity_widget: WidgetInput(
            widget=activity_widget,
            args={
                "message": llm_output,
                "function_name": data.function_name,
                "response": data.response,
            },
        )
    }
    widgets = add_ui_to_widget(widget_inputs=inp, version=version)
    output = BuildOutput(
        widgets_count=len(widgets),
        widgets=[w.model_dump(exclude_none=True) for w in widgets],
    )
    save_builder_output(context, output)
    return output
