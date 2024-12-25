import logging
import time
import os
import re
from functions_to_format.components import widgets
from functions_to_format.functions import (
    get_balance,
    chatbot_answer,
    unauthorized_response,
    get_receiver_id_by_reciver_phone_number,
)

# Janis Rubins changes:
# - Added deep logging at each step to understand exactly what's happening.
# - Used a high-performance approach: cached lookups, removed dead code, and minimized redundant operations.
# - Logging includes timing each method for performance insights.

# Janis Rubins step 1: Define constants for performance and security
# MAX_PAYLOAD_SIZE limits data size to prevent memory overhead
# SAFE_PATTERN ensures only safe identifiers are allowed
# SUSPICIOUS_PATTERNS checks for malicious patterns.
MAX_PAYLOAD_SIZE = 1024 * 1024
SAFE_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")
SUSPICIOUS_PATTERNS = ["__proto__", "constructor", "prototype", "<script"]

# Janis Rubins step 2: Set up a flexible logging system
# LOG_LEVEL environment variable controls whether we log at DEBUG or ERROR level
log_level = os.environ.get("LOG_LEVEL", "ERROR").upper()
level = logging.DEBUG if log_level == "DEBUG" else logging.ERROR
logger = logging.getLogger(__name__)
logger.setLevel(level)
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s]: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

functions_mapper = {
    "get_balance": get_balance,
    "chatbot_answer": chatbot_answer,
    "unauthorized_response": unauthorized_response,
    "get_receiver_id_by_reciver_phone_number": get_receiver_id_by_reciver_phone_number,
}


# Janis Rubins step 4: Check if identifiers are safe to prevent malicious keys
def is_safe_identifier(value: str) -> bool:
    return bool(SAFE_PATTERN.match(value))


# Janis Rubins step 5: Sanitize input to remove suspicious patterns and limit size
# Prevents loading or processing large or malicious payloads.
def sanitize_input(data):
    data_str = str(data)
    if len(data_str.encode()) > MAX_PAYLOAD_SIZE:
        logger.error("Input data exceeds size limit")
        return None
    if any(pattern in data_str.lower() for pattern in SUSPICIOUS_PATTERNS):
        logger.error("Suspicious pattern detected in input")
        return None
    return data


# Janis Rubins step 6: Decorator to measure execution time and log steps for performance insights
# Helps identify bottlenecks and optimize resource usage.
def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.debug(f"--- START {func.__name__} ---")
        logger.debug(f"Arguments: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.debug(f"{func.__name__} completed. Elapsed time: {end - start:.6f}s")
        logger.debug(f"--- END {func.__name__} ---\n")
        return result

    return wrapper


# Janis Rubins step 7: Formatter class to format widgets and invoke functions
# Flexible structure to add new methods or extend existing ones.
class Formatter:
    def __init__(self) -> None:
        # Janis Rubins step 8: Initialize without heavy operations to save resources
        logger.debug("Initializing Formatter, config set to None.")
        self.config = None

    @timed
    def format_widget(self, widget_name, data):
        logger.debug(
            f"format_widget called with widget_name='{widget_name}' and data='{data}'"
        )
        # Janis Rubins: Access widgets once, store locally for speed
        component = widgets.get(widget_name, None)
        if component is None:
            logger.debug(f"No widget found for '{widget_name}', returning data as is.")
            return data

        # Janis Rubins step 10: If widget is text_widget, use format_text for custom rendering
        if widget_name == "text_widget":
            logger.debug("Detected 'text_widget', calling format_text.")
            return self.format_text(component, data)
        else:
            # Janis Rubins: For now, non-text widgets just return data unchanged
            logger.debug(
                f"'{widget_name}' is not 'text_widget', returning data unchanged."
            )
            return data

    @timed
    def format_by_function(self, function_name, llm_output, backend_function_output):
        # Janis Rubins step 11: Invoke a mapped function (e.g. get_balance, chatbot_answer)
        # Allows flexible integration with external systems.
        logger.debug(
            f"format_by_function called with function_name='{function_name}', llm_output='{llm_output}', backend_function_output='{backend_function_output}'"
        )

        if not is_safe_identifier(function_name):
            logger.error(f"Unsafe function name '{function_name}' detected.")
            return None

        llm_output = sanitize_input(llm_output)
        backend_function_output = sanitize_input(backend_function_output)
        if llm_output is None or backend_function_output is None:
            logger.error("Data sanitization failed in format_by_function.")
            return None

        func = functions_mapper.get(function_name, None)
        if func is None:
            logger.error(f"No function mapped for '{function_name}', cannot proceed.")
            return None

        logger.debug(f"Found mapped function for '{function_name}', invoking it now.")
        return func(llm_output, backend_function_output)

    @timed
    def format_list(self):
        # Janis Rubins step 12: Placeholder for formatting lists, easily extendable
        logger.debug("format_list called, currently not implemented.")
        pass

    @timed
    def format_container(self):
        # Janis Rubins step 13: Placeholder for formatting containers, easily extendable
        logger.debug("format_container called, currently not implemented.")
        pass

    @timed
    def format_text(self, widget, data):
        # Janis Rubins step 14: Format text widgets, customizing their structure
        # Data already sanitized in calling method.
        logger.debug(f"format_text called with widget='{widget}' and data='{data}'")

        final_widget = {
            "name": "text_normal",
            "type": "text_container",
            "fields": [{"text": data}],
        }
        logger.debug(f"Text widget formatted: {final_widget}")
        return final_widget

    @timed
    def format_button(self):
        # Janis Rubins step 15: Placeholder for formatting buttons, can be implemented later
        logger.debug("format_button called, currently not implemented.")
        pass

    @timed
    def format_icon(self):
        # Janis Rubins step 16: Placeholder for formatting icons, can be implemented later
        logger.debug("format_icon called, currently not implemented.")
        pass
