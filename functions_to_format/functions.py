import jsonschema
import jsonschema.exceptions
from functions_to_format.components import widgets
import genson

# Janis Rubins: precompile validator to avoid repeated schema parsing
balance_card_schema = widgets.get("balance_card", None)
balance_card_validator = None
if balance_card_schema is not None:
    balance_card_validator = jsonschema.Draft7Validator(balance_card_schema)  # Janis Rubins: validator created once


def chatbot_answer(llm_output, backend_output):
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data
    return {
        "schema": widgets["text_widget"],
        "data": llm_output,
    }


def get_balance(llm_output, backend_output):
    # Janis Rubins: use precompiled validator if available to avoid repeated validation overhead
    if balance_card_validator is not None:
        try:
            balance_card_validator.validate(backend_output)  # Janis Rubins: faster validation
        except jsonschema.exceptions.ValidationError as e:
            print(e)
            return None
    else:
        # Janis Rubins: fallback to original validation if no precompiled validator
        try:
            jsonschema.validate(backend_output, schema=widgets["balance_card"])
        except Exception as e:
            print(e)
            return None

    # Janis Rubins: return schema and data if valid
    return {
        "schema": widgets["balance_card"],
        "data": backend_output,
    }



# {
#   "$schema": "http://json-schema.org/draft-07/schema#",
#   "type": "object",
#   "properties": {
#     "question": {
#       "type": "string",
#       "description": "The prompt asking the user to make a selection."
#     },
#     "components": {
#       "type": "array",
#       "description": "List of predefined card components for selection.",
#       "items": {
#         "type": "object",
#         "properties": {
#           "id": {
#             "type": "string",
#             "description": "Unique identifier for the card."
#           },
#           "balance": {
#             "type": "integer",
#             "description": "Current balance displayed on the card."
#           },
#           "type": {
#             "type": "string",
#             "description": "Type or label of the card, e.g., salary, savings."
#           },
#           "provider": {
#             "type": "string",
#             "description": "The bank or provider associated with the card."
#           },
#           "last_digits": {
#             "type": "string",
#             "pattern": "\\d{4}",
#             "description": "The last four digits of the card number."
#           },
#           "background": {
#             "type": "string",
#             "description": "The background style or theme of the card, e.g., image URL or pattern ID."
#           }
#         },
#         "required": ["id", "balance", "type", "provider", "last_digits"]
#       }
#     },
#     "cancel_button": {
#       "type": "object",
#       "description": "Cancel button configuration.",
#       "properties": {
#         "text": {
#           "type": "string",
#           "description": "The text displayed on the cancel button."
#         },
#         "action": {
#           "type": "string",
#           "description": "The action triggered by the cancel button, e.g., close or navigate back."
#         }
#       },
#       "required": ["text", "action"]
#     }
#   },
#   "required": ["question", "components", "cancel_button"]
# }
