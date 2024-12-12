from functions_to_format.components import widgets
from functions_to_format.functions import get_balance, chatbot_answer


functions_mapper = {"get_balance": get_balance, "chatbot_answer": chatbot_answer}


class Formatter:
    def __init__(self) -> None:
        self.config = None

    def format_widget(self, widget_name, data):
        components = widgets[widget_name]
        if widget_name == "text_widget":
            return self.format_text(components, data)
        return data
        widget = widgets[widget_name]

    def format_by_function(self, function_name, llm_output, backend_function_output):
        return functions_mapper[function_name](llm_output, backend_function_output)

    def format_list(self):
        pass

    def format_container(self):
        pass

    def format_text(self, widget, data):
        widget = {"name": "text_normal", "type": "text_container", "fields": ["text"]}

        widget["fields"][0] = {"text": data}
        return widget

    def format_button(self):
        pass

    def format_icon(self):
        pass
