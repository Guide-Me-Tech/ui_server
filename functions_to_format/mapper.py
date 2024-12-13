import logging
import time

from functions_to_format.components import widgets
from functions_to_format.functions import get_balance, chatbot_answer

# Janis Rubins changes: 
# - Added deep logging at each step to understand exactly what's happening.
# - Used a high-performance approach: cached lookups, removed dead code, and minimized redundant operations.
# - Logging includes timing each method for performance insights.

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

functions_mapper = {"get_balance": get_balance, "chatbot_answer": chatbot_answer}


def timed(func):
    # Janis Rubins: decorator to measure execution time of functions for performance insights
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


class Formatter:
    def __init__(self) -> None:
        # Janis Rubins: config currently unused, but we keep it for future expansions
        logger.debug("Initializing Formatter instance, config set to None.")
        self.config = None

    @timed
    def format_widget(self, widget_name, data):
        logger.debug(f"format_widget called with widget_name='{widget_name}' and data='{data}'")
        # Janis Rubins: Access widgets once, store locally for speed
        component = widgets.get(widget_name, None)
        if component is None:
            logger.debug(f"No widget found for '{widget_name}', returning data as is.")
            return data

        if widget_name == "text_widget":
            logger.debug("Detected 'text_widget', calling format_text.")
            return self.format_text(component, data)
        else:
            # Janis Rubins: For now, non-text widgets just return data unchanged
            logger.debug(f"'{widget_name}' is not 'text_widget', returning data unchanged.")
            return data

    @timed
    def format_by_function(self, function_name, llm_output, backend_function_output):
        logger.debug(f"format_by_function called with function_name='{function_name}', llm_output='{llm_output}', backend_function_output='{backend_function_output}'")
        func = functions_mapper.get(function_name, None)
        if func is None:
            logger.error(f"No function mapped for '{function_name}', cannot proceed.")
            return None
        logger.debug(f"Found mapped function for '{function_name}', invoking it now.")
        return func(llm_output, backend_function_output)

    @timed
    def format_list(self):
        logger.debug("format_list called, currently not implemented.")
        pass

    @timed
    def format_container(self):
        logger.debug("format_container called, currently not implemented.")
        pass

    @timed
    def format_text(self, widget, data):
        logger.debug(f"format_text called with widget='{widget}' and data='{data}'")
        final_widget = {
            "name": "text_normal",
            "type": "text_container",
            "fields": [{"text": data}]
        }
        logger.debug(f"Text widget formatted: {final_widget}")
        return final_widget

    @timed
    def format_button(self):
        logger.debug("format_button called, currently not implemented.")
        pass

    @timed
    def format_icon(self):
        logger.debug("format_icon called, currently not implemented.")
        pass
