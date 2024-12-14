import jsonschema
import jsonschema.exceptions
from functions_to_format.components import widgets
import genson
import json

# Janis Rubins: precompile validator to avoid repeated schema parsing
balance_card_schema = widgets.get("balance_card", None)
balance_card_validator = None
if balance_card_schema is not None:
    balance_card_validator = jsonschema.Draft7Validator(
        balance_card_schema
    )  # Janis Rubins: validator created once


def chatbot_answer(llm_output, backend_output):
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data
    return {
        "schema": widgets["text_widget"],
        "data": llm_output,
    }


cards = [
    {
        "pan": "************7478",
        "balance": "",
        "bankIssuer": "SmartBank",
        "processingSystem": "humo",
        "cardDetails": {
            "cardDetailsId": 7846,
            "cardName": "Smartbank Virtual",
            "cardColor": "0006",
            "cardIsPrimary": False,
        },
    },
    {
        "pan": "************5289",
        "balance": 0,
        "bankIssuer": "Kapital",
        "processingSystem": "humo",
        "cardDetails": {
            "cardDetailsId": 23192,
            "cardName": "kapital",
            "cardColor": "0000",
            "cardIsPrimary": False,
        },
    },
    {
        "pan": "************7704",
        "balance": 1001036,
        "bankIssuer": "SmartBank",
        "processingSystem": "humo",
        "cardDetails": {
            "cardDetailsId": 42946,
            "cardName": "Smartbank fiz",
            "cardColor": "0000",
            "cardIsPrimary": False,
        },
    },
    {
        "pan": "************9710",
        "balance": 0,
        "bankIssuer": "BRB",
        "processingSystem": "humo",
        "cardDetails": {
            "cardDetailsId": 166412,
            "cardName": "brb",
            "cardColor": "0000",
            "cardIsPrimary": False,
        },
    },
]


def get_balance(llm_output, backend_output):
    # Janis Rubins: use precompiled validator if available to avoid repeated validation overhead
    #  preprocess backend output:
    output = [
        llm_output,
    ]
    backend_output_processed = []
    for i, card_info in enumerate(backend_output):
        backend_output_processed.append(
            {
                "index": i + 1,
                "own_card_container": {
                    "masked_card_pan": card_info["pan"],
                    "card_type": card_info["processingSystem"],
                    "balance": card_info["balance"]
                    if type(card_info["balance"]) is int
                    else 0,
                    "card_name": card_info["cardDetails"]["cardName"],
                },
            }
        )
    output = [{"text": llm_output}, backend_output_processed]
    print("Output", output)
    # if balance_card_validator is not None:
    #     try:
    #         balance_card_validator.validate(output)  # Janis Rubins: faster validation
    #     except jsonschema.exceptions.ValidationError as e:
    #         print(e)
    #         return None

    # else:
    # Janis Rubins: fallback to original validation if no precompiled validator
    try:
        jsonschema.validate(output, schema=widgets["balance_info"])
    except Exception as e:
        print(e)
        return (
            "Error building the widget ---- the backend output is not valid for the widget schema "
            + str(e)
        )

    # Janis Rubins: return schema and data if valid
    return {
        "schema": widgets["balance_info"],
        "data": output,
    }


def get_receiver_id_by_reciver_phone_number(llm_output, backend_output):
    output = []
    backend_output_processed = []
    # process backed_output
    #  {
    #     #     "pan": "3b1cdf68-cd9f-496a-b756-cd7884b5b9f9",
    #     #     "name": "A. H",
    #     #     "processing": "uzcard",
    #     #     "mask": "561468******9682"
    #     # },
    print(backend_output)
    # if type(backend_output) is str:
    #     backend_output = json.loads(backend_output)
    # for i in backend_output:
    #     print(i)
    for i, card_info in enumerate(backend_output):
        print(f"Card {i + 1} info: ", card_info)
        backend_output_processed.append(
            {
                "index": i + 1,
                "other_card_container": {
                    "masked_card_pan": card_info["mask"],
                    "card_owner": card_info["name"],
                    "provider": card_info["processing"],
                },
            }
        )

    output = [
        {"text": llm_output},
        backend_output_processed,
        [{"text": "ok"}, {"text": "cancel"}],
    ]
    try:
        jsonschema.validate(output, schema=widgets["card_other_list_widget"])
    except Exception as e:
        return (
            "Error building the widget ---- the backend output is not valid for the widget schema: "
            + str(e)
        )

    return {"schema": widgets["card_other_list_widget"], "data": output}


def unauthorized_response(llm_output, backend_output):
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data
    return {
        "schema": widgets["text_widget"],
        "data": llm_output,
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
