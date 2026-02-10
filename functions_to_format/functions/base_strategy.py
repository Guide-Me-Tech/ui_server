"""Strategy Design Pattern base for function handlers.

The Strategy pattern separates the *what* (which widgets to build, how to
parse backend data) from the *how* (the common workflow of building output
and saving).

Each function handler is a concrete strategy that only needs to implement
build_widget_inputs() to describe what widgets should be built.
The base class handles the rest: calling add_ui_to_widget, creating
BuildOutput, and calling save_builder_output.
"""

from abc import ABC, abstractmethod
from typing import Callable, Dict, List, Optional

from models.build import BuildOutput
from models.context import Context

from .general import WidgetInput, TextWidget, add_ui_to_widget
from .general.text import build_text_widget
from .general.utils import save_builder_output


class FunctionStrategy(ABC):
    """Abstract base for all function handler strategies.

    Subclasses implement build_widget_inputs to declare the mapping from
    builder functions to their WidgetInput configurations. The common
    execution workflow (widget building, output creation, persistence) is
    handled by execute.

    Instances are callable, so they can be used directly in
    functions_mapper as drop-in replacements for plain handler functions.
    """

    @abstractmethod
    def build_widget_inputs(
        self, context: Context
    ) -> Dict[Callable, WidgetInput]:
        """Return the widget-builder to WidgetInput mapping for this handler."""
        ...

    def execute(self, context: Context) -> BuildOutput:
        """Run the common workflow: build widgets, assemble output, save.

        Override this method only when the handler needs non-standard
        post-processing (e.g. embedding extra widgets from sub-handlers).
        """
        widget_inputs = self.build_widget_inputs(context)
        return self._build_and_save(context, widget_inputs)

    def __call__(self, context: Context) -> BuildOutput:
        """Allow strategy instances to be called like plain functions."""
        return self.execute(context)

    # ------------------------------------------------------------------
    # Helpers available to subclasses
    # ------------------------------------------------------------------

    @staticmethod
    def _build_and_save(
        context: Context,
        widget_inputs: Dict[Callable, WidgetInput],
        extra_widget_dicts: Optional[List[dict]] = None,
    ) -> BuildOutput:
        """Shared helper: build widgets, assemble BuildOutput, save, return."""
        widgets = add_ui_to_widget(widget_inputs, context.version)
        all_widgets: List[dict] = [
            w.model_dump(exclude_none=True) for w in widgets
        ]

        if extra_widget_dicts:
            base_order = len(all_widgets) + 1
            for idx, w_dict in enumerate(extra_widget_dicts):
                all_widgets.append({**w_dict, "order": base_order + idx})

        output = BuildOutput(
            widgets_count=len(all_widgets),
            widgets=all_widgets,
        )
        save_builder_output(context, output)
        return output

    @staticmethod
    def make_text_input(llm_output: str, order: int = 1):
        """Convenience: create a (builder, WidgetInput) pair for a text widget."""
        return (
            build_text_widget,
            WidgetInput(
                widget=TextWidget(order=order, values=[{"text": llm_output}]),
                args={"text": llm_output},
            ),
        )
