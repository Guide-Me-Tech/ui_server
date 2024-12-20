import os
import sys
import logging
from typing import Any, Dict, List, Optional
import json

"""
Why this code is needed:
- After adapters transform raw data into a standardized structure, we need to dynamically build UI.
- The UI builder takes adapted data, uses "widgets" and other components to create a final UI representation.
- Configuration from environment variables ensures we can easily change the output format, widget usage, and logic without code changes.
- Detailed logging allows full traceability of each step.

Key Environment Variables:
- UI_BUILDER_LOG_LEVEL (default: ERROR): Controls verbosity of builder logs.
- UI_BUILDER_OUTPUT_FORMAT (default: "json"): The final UI output format (e.g., "json", "dict", "html" - you can extend as needed).
- UI_BUILDER_WIDGET_MAPPING (default: ""): A JSON string or comma-separated keys that define how data fields map to widget names.
- UI_BUILDER_ENABLE_CACHING (default: "false"): If "true", enable caching of widget layouts to save CPU and RAM.
- UI_BUILDER_DEFAULT_WIDGET (default: "text_widget"): Which widget to use if no mapping found.
- UI_BUILDER_RESOURCE_SAVING_MODE (default: "true"): If "true", tries to minimize overhead, skip unnecessary steps.

This code flexible and resource-friendly by:
- Only loading configs once.
- Using minimal overhead checks.
- Allowing caching if enabled.

We assume `widgets` is available from functions_to_format.components (already defined), or we do a lazy import.
If not available, we show how to integrate.

Steps are clearly logged (Janis Rubins step X).
"""

# Janis Rubins step 1: Load environment variables for configuration
UI_BUILDER_LOG_LEVEL = os.environ.get("UI_BUILDER_LOG_LEVEL", "ERROR").upper()
UI_BUILDER_OUTPUT_FORMAT = os.environ.get("UI_BUILDER_OUTPUT_FORMAT", "json").lower()
UI_BUILDER_WIDGET_MAPPING = os.environ.get("UI_BUILDER_WIDGET_MAPPING", "")
UI_BUILDER_ENABLE_CACHING = os.environ.get("UI_BUILDER_ENABLE_CACHING", "false").lower() == "true"
UI_BUILDER_DEFAULT_WIDGET = os.environ.get("UI_BUILDER_DEFAULT_WIDGET", "text_widget")
UI_BUILDER_RESOURCE_SAVING_MODE = os.environ.get("UI_BUILDER_RESOURCE_SAVING_MODE", "true").lower() == "true"

# Janis Rubins step 2: Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(UI_BUILDER_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

# Janis Rubins step 3: Attempt to import widgets from functions_to_format.components
# If not found, fallback to empty dict or handle gracefully.
try:
    from functions_to_format.components import widgets
except ImportError:
    logger.warning("Could not import widgets from functions_to_format.components. Using empty widgets dict.")
    widgets = {}  # fallback, but normally we should have widgets defined.

# Janis Rubins step 4: Parse UI_BUILDER_WIDGET_MAPPING
# It could be a JSON or comma-separated. We choose JSON for flexibility.
# Example: {"title": "text_widget", "items": "card_own_list_widget"}
mapping: Dict[str, str] = {}
if UI_BUILDER_WIDGET_MAPPING.strip():
    try:
        # Attempt JSON parse first
        mapping = json.loads(UI_BUILDER_WIDGET_MAPPING)
        if not isinstance(mapping, dict):
            logger.warning("UI_BUILDER_WIDGET_MAPPING is not a dict. Ignoring.")
            mapping = {}
    except json.JSONDecodeError:
        logger.warning("UI_BUILDER_WIDGET_MAPPING not valid JSON, ignoring.")
        mapping = {}

# Janis Rubins step 5: Caching mechanism (if enabled)
# We could keep a cache of final UI structures keyed by a hash of input data.
ui_cache = {}

def cache_key_for_data(data: Dict[str, Any]) -> str:
    # Minimal overhead hash: convert to JSON string and hash it
    # For speed, just use the JSON string as key if stable sorting done by json.dumps with sort_keys=True
    data_str = json.dumps(data, sort_keys=True)
    return data_str  # In production, might use a real hash like hashlib.sha256(data_str.encode()).hexdigest() for shorter keys.


class DynamicUIBuilder:
    """
    Janis Rubins step 6: DynamicUIBuilder class:
    Methods:
    - build_ui(data: dict) -> str or dict: Main entry point.
      Takes adapted data and produces final UI based on widget mapping and output format.
    - Uses environment-driven logic to map data fields to widgets.
    - Minimizes overhead by skipping steps if resource saving mode is on and no complexity needed.
    - Logs each step for transparency.
    """

    def __init__(self):
        # Janis Rubins step 7: Any initialization if needed
        # For now, just confirm configuration
        logger.debug("DynamicUIBuilder initialized with the following configuration:")
        logger.debug(f"OUTPUT_FORMAT={UI_BUILDER_OUTPUT_FORMAT}, MAPPING={mapping}, CACHING={UI_BUILDER_ENABLE_CACHING}, DEFAULT_WIDGET={UI_BUILDER_DEFAULT_WIDGET}, RESOURCE_SAVING_MODE={UI_BUILDER_RESOURCE_SAVING_MODE}")

    def build_ui(self, data: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        # Janis Rubins step 8: Log start of UI build process
        logger.debug("DynamicUIBuilder: Starting UI construction from adapted data.")

        # Janis Rubins step 9: Check cache if enabled
        if UI_BUILDER_ENABLE_CACHING:
            ck = cache_key_for_data(data)
            if ck in ui_cache:
                logger.debug("DynamicUIBuilder: Returning UI from cache to save resources.")
                return ui_cache[ck]

        # Janis Rubins step 10: Construct UI structure.
        # We'll create a UI that is a list of widgets or a structure determined by data keys.
        # For each key in data, try to find a widget from mapping or use default.
        # The actual logic depends on what data structure we have from adapters.
        # We'll assume adapted data is already stable and well-defined.

        ui_structure = self._build_ui_structure(data)

        # Janis Rubins step 11: Format output according to UI_BUILDER_OUTPUT_FORMAT
        final_output = self._format_output(ui_structure)

        # Janis Rubins step 12: Store in cache if enabled
        if UI_BUILDER_ENABLE_CACHING:
            ui_cache[ck] = final_output

        logger.debug("DynamicUIBuilder: UI construction completed.")
        return final_output

    def _build_ui_structure(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Janis Rubins step 13: Internal method to build UI structure.
        For each key in data, we determine a widget, create a UI element from it.
        Minimizing overhead: If data is large, only process keys that matter.
        If resource saving mode is on, skip unnecessary transformations.

        We'll assume 'data' is a dict that may have fields like 'title', 'content', etc.
        We'll produce a UI dict like:
        {
          "ui": [
             { "widget": "text_widget", "data": ... },
             ...
          ]
        }
        """

        # Janis Rubins step 14: Create a UI list
        ui_elements: List[Dict[str, Any]] = []

        # If resource saving mode is on, do minimal processing.
        # If off, we could add more verbose steps.
        keys_to_process = data.keys()

        for key in keys_to_process:
            widget_name = mapping.get(key, UI_BUILDER_DEFAULT_WIDGET)
            widget = widgets.get(widget_name)
            if widget is None:
                # If no widget found, fallback to some minimal representation
                logger.debug(f"No widget found for {widget_name}, using default text_widget-like structure.")
                ui_elements.append({
                    "widget": widget_name,
                    "data": data[key]
                })
            else:
                # Janis Rubins step 15: If widget found, we could call some widget logic (if defined)
                # For now, we just attach data to widget_info.
                # In a real scenario, widget might be a schema or function. We'll just store data.
                ui_elements.append({
                    "widget": widget_name,
                    "data": data[key]
                })
                logger.debug(f"Assigned widget {widget_name} to key '{key}'.")
        
        # Janis Rubins step 16: The final UI structure
        # Could be more complex if ENV says so.
        ui_structure = {"ui": ui_elements}
        logger.debug("UI structure built successfully.")
        return ui_structure

    def _format_output(self, ui_structure: Dict[str, Any]) -> Union[str, Dict[str, Any]]:
        """
        Janis Rubins step 17: Format output according to UI_BUILDER_OUTPUT_FORMAT.
        Supported: "json", "dict", future "html" or other.
        If resource saving mode on and format is json, just do json dumps once.
        """
        if UI_BUILDER_OUTPUT_FORMAT == "json":
            # Janis Rubins step 18: Return JSON string
            output_str = json.dumps(ui_structure, ensure_ascii=False)
            logger.debug("UI formatted as JSON.")
            return output_str
        elif UI_BUILDER_OUTPUT_FORMAT == "dict":
            # Janis Rubins step 19: Return the dict directly
            logger.debug("UI returned as dict.")
            return ui_structure
        else:
            # Janis Rubins step 20: If unknown format, fallback to dict
            logger.warning(f"Unknown UI_BUILDER_OUTPUT_FORMAT={UI_BUILDER_OUTPUT_FORMAT}, returning dict.")
            return ui_structure

# Janis Rubins step 21: Example usage (commented out):
# builder = DynamicUIBuilder()
# final_ui = builder.build_ui({"title":"Hello", "content":{"text":"World"}})
# print(final_ui)
#
# With ENV changes, we can alter widgets, format, caching, etc. without code modifications.
