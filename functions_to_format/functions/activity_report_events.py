"""Orchestration layer for function-call / function-response activity reports.

*  Pure UI builders live in ``activity_report.py``.
*  This module wires context → UI builders and, for responses whose
   ``function_name`` has a known handler, embeds the rich widget produced
   by that handler alongside the activity report.
"""

from typing import Callable, Dict, List, Optional

from .general import Widget, WidgetInput
from models.build import BuildOutput
from models.context import Context

from .base_strategy import FunctionStrategy
from .activity_report import (
    FunctionCallBackendOutput,
    FunctionResponseBackendOutput,
    build_function_call_activity_widget,
    build_function_response_activity_widget,
)

# ---------------------------------------------------------------------------
# Lazy-loaded registry: function_name  →  handler(Context) → BuildOutput
# ---------------------------------------------------------------------------

_response_ui_registry: Optional[Dict[str, Callable[[Context], BuildOutput]]] = None


def _get_response_ui_registry() -> Dict[str, Callable[[Context], BuildOutput]]:
    """Return (and lazily initialise) the map of function names whose
    response data can be turned into a rich widget by the existing handler.

    Lazy importing avoids circular dependencies with ``functions.py``."""
    global _response_ui_registry
    if _response_ui_registry is not None:
        return _response_ui_registry

    from .balance import get_balance, get_home_balances
    from .weather import get_weather_info
    from .news import get_news
    from .notification import get_notifications
    from .contact import get_contact
    from .products import get_products, search_products
    from .payment import (
        get_categories,
        get_fields_of_supplier,
        get_suppliers_by_category,
    )
    from .mortgage import calculate_mortgage

    _response_ui_registry = {
        "get_balance": get_balance,
        "get_home_balances": get_home_balances,
        "get_weather_info": get_weather_info,
        "get_categories": get_categories,
        # "get_fields_of_supplier": get_fields_of_supplier,
        "get_suppliers_by_category": get_suppliers_by_category,
        # "get_news": get_news,
        # "get_notifications": get_notifications,
        # "get_contact": get_contact,
        "get_products": get_products,
        "search_products": search_products,
        "calculate_mortgage": calculate_mortgage,
    }
    return _response_ui_registry


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _try_build_embedded_ui(
    function_name: str,
    response: dict,
    parent_context: Context,
) -> Optional[List[dict]]:
    """If *function_name* has a known UI handler, call it with *response* as
    ``backend_output`` and return its non-text widget dicts.

    * Text widgets are filtered out because the activity report already
      shows the LLM message.
    * Returns ``None`` when the function is not registered or the handler
      fails (failures are logged, never raised).
    """
    function_name = function_name.replace("_wrapper", "")
    registry = _get_response_ui_registry()
    handler = registry.get(function_name)
    if handler is None:
        return None

    synthetic_ctx = Context(
        llm_output="",  # empty → text widgets are skipped by add_ui_to_widget
        backend_output=response,
        version=parent_context.version,
        language=parent_context.language,
        api_key=parent_context.api_key,
        logger_context=parent_context.logger_context,
    )

    try:
        result: BuildOutput = handler(context=synthetic_ctx)
    except Exception as exc:
        parent_context.logger_context.logger.warning(
            "embedded_ui_build_failed",
            function_name=function_name,
            error=str(exc),
        )
        return None

    # Keep only real UI widgets (drop text_widget duplicates)
    embedded: List[dict] = []
    for w in result.widgets:
        w_dict = w if isinstance(w, dict) else w.model_dump(exclude_none=True)
        if w_dict.get("type") == "text_widget":
            continue
        embedded.append(w_dict)

    return embedded if embedded else None


# ---------------------------------------------------------------------------
# Public handlers (registered in functions_mapper)
# ---------------------------------------------------------------------------


class FunctionCallActivityRecord(FunctionStrategy):
    """Strategy for function-call activity event UI."""

    def build_widget_inputs(self, context):
        data = FunctionCallBackendOutput(
            function_name=context.backend_output.get("function_name", ""),
            arguments=context.backend_output.get("arguments", {}),
        )
        return {
            build_function_call_activity_widget: WidgetInput(
                widget=Widget(
                    name="function_call_activity_widget",
                    type="function_call_activity_widget",
                    order=1,
                    layout="vertical",
                    fields=["function_call_activity"],
                ),
                args={
                    "message": context.llm_output,
                    "function_name": data.function_name,
                    "arguments": data.arguments,
                    "language": context.language,
                },
            ),
        }


function_call_activity_record = FunctionCallActivityRecord()


class FunctionResponseActivityRecord(FunctionStrategy):
    """Strategy for function-response activity event UI.

    When function_name matches a known handler, embeds rich widgets
    alongside the activity report.
    """

    def build_widget_inputs(self, context):
        data = FunctionResponseBackendOutput(
            function_name=context.backend_output.get("function_name", ""),
            response=context.backend_output.get("response", {}),
        )
        return {
            build_function_response_activity_widget: WidgetInput(
                widget=Widget(
                    name="function_response_activity_widget",
                    type="function_response_activity_widget",
                    order=1,
                    layout="vertical",
                    fields=["function_response_activity"],
                ),
                args={
                    "message": context.llm_output,
                    "function_name": data.function_name,
                    "response": data.response,
                    "language": context.language,
                },
            ),
        }

    def execute(self, context):
        data = FunctionResponseBackendOutput(
            function_name=context.backend_output.get("function_name", ""),
            response=context.backend_output.get("response", {}),
        )
        embedded = _try_build_embedded_ui(
            function_name=data.function_name,
            response=data.response,
            parent_context=context,
        )
        widget_inputs = self.build_widget_inputs(context)
        return self._build_and_save(context, widget_inputs, extra_widget_dicts=embedded)


function_response_activity_record = FunctionResponseActivityRecord()
