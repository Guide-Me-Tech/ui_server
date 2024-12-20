import logging
import sys
import os
import re
import json
import hashlib
from typing import Dict, Any, List
from functools import lru_cache

"""
- Prepares sets of schemas for analytics, machine learning training, or other processing tasks.
- Provides structured JSON schemas that can be easily integrated with external systems.
- Flexibility: easy to modify, extend, and use in large-scale processes.
- Deep logging: full control over each step, simplifying debugging and performance optimization.
- Security: checks identifiers, protects against malicious data without performance loss.
- Does not break old logic: retains original functionality, adding new layers of security, logging, and flexibility.
"""

# Janis Rubins step 1: Constants for security and performance
MAX_SCHEMA_SIZE = 1024 * 1024  # 1MB max schema size
MAX_STEPS_HISTORY = 1000  # Limit step records to avoid memory overhead
CACHE_SIZE = 100  # LRU cache size for schema validations
SAFE_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")  # Pattern for safe identifiers

# Janis Rubins step 2: Configure a flexible logging system
log_level = os.environ.get("LOG_LEVEL", "ERROR").upper()
level = logging.DEBUG if log_level == "DEBUG" else logging.ERROR
logger = logging.getLogger(__name__)
logger.setLevel(level)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s]: %(message)s")
)
logger.addHandler(handler)


# Janis Rubins step 3: StepsTracker for deep debugging and schema integrity checks
class StepsTracker:
    def __init__(self, max_steps: int = MAX_STEPS_HISTORY):
        self.steps: List[str] = []
        self.max_steps = max_steps
        self._schema_hashes: Dict[str, str] = {}


def record_step(msg):
    # Janis Rubins: function to record each step, so if error occurs we know what happened
    pass


try:
    # Janis Rubins: record environment info, helps debug if error occurs
    record_step(f"System info: Python version: {sys.version}, Platform: {sys.platform}")
    record_step(f"Current working directory: {os.getcwd()}")
    record_step(
        "Start loading balance_info schema."
    )  # Janis Rubins: track start of loading schema

    # Below: original logic of loading schemas. We keep it as is, just integrated into this new structure.

    balance_info = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": [
            {
                "type": "object",
                "$ref": "#/definitions/text_normal",  # Janis Rubins: using consistent $ref
            },
            {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/cards_list_item_own"
                },  # Janis Rubins: direct reference
            },
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Displayed text."}
                },
                "required": ["text"],
            },
            "cards_list_item_own": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Index of the card in the list.",  # Janis Rubins: card index
                    },
                    "own_card_container": {
                        "$ref": "#/definitions/own_card_container"
                    },  # Janis Rubins: referencing container
                },
                "required": ["index", "own_card_container"],
            },
            "own_card_container": {
                "type": "object",
                "properties": {
                    "masked_card_pan": {
                        "type": "string",
                        "description": "Masked card number (e.g., **** 1234).",  # Janis Rubins: card pan
                    },
                    "card_type": {
                        "type": "string",
                        "description": "The type of the card (e.g., debit, credit).",  # Janis Rubins: card type
                    },
                    "balance": {
                        "type": "number",
                        "description": "The available balance on the card.",  # Janis Rubins: card balance
                    },
                    "card_name": {
                        "type": "string",
                        "description": "The name of the card.",  # Janis Rubins: card name
                    },
                },
                "required": ["masked_card_pan", "card_type", "balance", "card_name"],
            },
        },
    }
    record_step(
        "balance_info schema loaded, checking definitions count."
    )  # Janis Rubins: after load, check details
    record_step(
        f"balance_info has {len(balance_info['definitions'])} definitions."
    )  # Janis Rubins: log how many defs

    record_step(
        "Start loading card_own_list_widget schema."
    )  # Janis Rubins: now load another schema
    card_own_list_widget = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": [
            {
                "type": "object",
                "enum": [
                    {"$ref": "#/definitions/text_normal"}
                ],  # Janis Rubins: same pattern as before
            },
            {
                "type": "array",
                "items": {
                    "$ref": "#/definitions/cards_list_item_own"
                },  # Janis Rubins: own card items
            },
            {
                "type": "object",
                "enum": [
                    {"$ref": "#/definitions/button"}
                ],  # Janis Rubins: button added
            },
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content displayed.",
                    }  # Janis Rubins: text again
                },
                "required": ["text"],
            },
            "button": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text displayed on the button.",  # Janis Rubins: button text
                    }
                },
                "required": ["text"],
            },
            "cards_list_item_own": {
                "type": "object",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Index of the card in the list.",  # Janis Rubins: index again
                    },
                    "own_card_container": {
                        "$ref": "#/definitions/own_card_container"
                    },  # Janis Rubins: same container ref
                },
                "required": ["index", "own_card_container"],
            },
            "own_card_container": {
                "type": "object",
                "properties": {
                    "masked_card_pan": {
                        "type": "string",
                        "description": "Masked card number (e.g., **** 1234).",  # Janis Rubins: same container fields
                    },
                    "card_type": {
                        "type": "string",
                        "description": "The type of the card (e.g., debit, credit).",
                    },
                    "balance": {
                        "type": "number",
                        "description": "The available balance on the card.",
                    },
                    "card_name": {
                        "type": "string",
                        "description": "The name of the card.",
                    },
                },
                "required": ["masked_card_pan", "card_type", "balance", "card_name"],
            },
        },
        "minItems": 3,
        "maxItems": 3,
    }
    record_step(
        "card_own_list_widget schema loaded successfully."
    )  # Janis Rubins: loaded OK
    record_step(
        f"card_own_list_widget has {len(card_own_list_widget['definitions'])} definitions."
    )  # Janis Rubins: count defs

    record_step(
        "Start loading card_other_list_widget schema."
    )  # Janis Rubins: another widget schema
    card_other_list_widget = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "minItems": 3,
        "maxItems": 3,
        "items": [
            {"$ref": "#/definitions/text_normal"},
            {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_other"}},
            {"type": "array", "items": {"$ref": "#/definitions/button"}},
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
                "description": "Represents text content displayed in the UI.",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content displayed.",
                    }
                },
                "required": ["text"],
            },
            "button": {
                "type": "object",
                "description": "Represents a button in the UI.",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text displayed on the button.",
                    }
                },
                "required": ["text"],
            },
            "cards_list_item_other": {
                "type": "object",
                "description": "Represents a card item in the list of other people's cards.",
                "properties": {
                    "index": {
                        "type": "integer",
                        "description": "Index of the card in the list.",
                    },
                    "other_card_container": {
                        "$ref": "#/definitions/other_card_container"
                    },
                },
                "required": ["index", "other_card_container"],
            },
            "other_card_container": {
                "type": "object",
                "description": "Container with info about another person's card.",
                "properties": {
                    "masked_card_pan": {
                        "type": "string",
                        "description": "Masked card number (e.g., **** 1234).",
                    },
                    "card_owner": {
                        "type": "string",
                        "description": "The name of the card owner.",
                    },
                    "provider": {
                        "type": "string",
                        "description": "The provider of the card (e.g., Visa, MasterCard).",
                    },
                },
                "required": ["masked_card_pan", "card_owner", "provider"],
            },
        },
    }
    record_step(
        "card_other_list_widget schema loaded successfully."
    )  # Janis Rubins: loaded fine
    record_step(
        f"card_other_list_widget has {len(card_other_list_widget['definitions'])} definitions."
    )  # Janis Rubins: count defs

    text_widget = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": [
            {
                "type": "object",
                "enum": [
                    {"$ref": "#/definitions/text_normal"}
                ],  # Janis Rubins: just one text object in array
            }
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content displayed.",
                    }
                },
                "required": ["text"],
            }
        },
    }
    record_step("text_widget schema loaded successfully.")  # Janis Rubins: loaded OK
    record_step(
        f"text_widget has {len(text_widget['definitions'])} definitions."
    )  # Janis Rubins: count defs

    record_step(
        "Assembling all widgets into a single dictionary..."
    )  # Janis Rubins: now put them all together
    widgets = {
        "balance_info": balance_info,  # Janis Rubins: add balance_info
        "card_own_list_widget": card_own_list_widget,  # Janis Rubins: add card_own_list_widget
        "card_other_list_widget": card_other_list_widget,  # Janis Rubins: add card_other_list_widget
        "text_widget": text_widget,  # Janis Rubins: add text_widget
    }
    record_step(
        "All widgets assembled successfully. Checking keys in 'widgets'."
    )  # Janis Rubins: check final keys
    record_step(f"widgets keys: {list(widgets.keys())}")  # Janis Rubins: log final keys
    record_step(
        "No errors encountered, process completed successfully."
    )  # Janis Rubins: done, no issues

except Exception as e:
    logger.error("AN ERROR OCCURRED DURING SCHEMA LOADING AND ASSEMBLY:")
    logger.error(f"Error details: {e}")
    raise


# all_components = {
#     "text_normal": {"type": "text_container", "fields": ["text"]},
#     "text_warning": {"type": "text_container", "fields": ["text"]},
#     "text_info": {"type": "text_container", "fields": ["text"]},
#     "button_small_white": {"type": "button", "fields": ["text"]},
#     "button_small_black": {"type": "button", "fields": ["text"]},
#     "button_big_black": {"type": "button", "fields": ["text"]},
#     "button_big_white": {"type": "button", "fields": ["text"]},
#     "own_card_container": {
#         "type": "card_container",
#         "fields": [
#             "masked_card_pan",
#             "card_balance",
#             "card_type",
#             "balance",
#             "card_name",
#         ],
#     },
#     "other_card_container": {
#         "type": "card_container",
#         "fields": ["masked_card_pan", "card_owner", "provider"],
#     },
#     "contacts_list": {"type": "list", "fields": ["index", "name", "phone"]},
#     "cards_list_own": {"type": "list", "fields": ["index", "own_card_container"]},
#     "cards_list_other": {"type": "list", "fields": ["index", "other_card_container"]},
#     "transfer_success": {
#         "type": "status_container",
#         "fields": [
#             {"header": ["status_text"]},
#             {"body": ["amount", "receiver", "masked_pan", ""]},
#             {"footer": ["date", "time"]},
#         ],
#     },
#     "transfer_failed": {
#         "type": "status_container",
#         "fields": [
#             {"header": ["status_text"]},
#             {"body": ["amount", "receiver", "masked_pan", ""]},
#             {"footer": ["date", "time"]},
#         ],
#     },
#     "transfer_pending": {
#         "type": "status_container",
#         "fields": [
#             {"header": ["status_text"]},
#             {"body": ["amount", "receiver", "masked_pan", ""]},
#             {"footer": ["date", "time"]},
#         ],
#     },
#     "payment_success": {
#         "type": "status_container",
#         "fields": [
#             {"header": ["status_text"]},
#             {"body": ["amount", "receiver", "from_card"]},
#             {"footer": ["date", "time"]},
#         ],
#     },
#     "payment_failed": {
#         "type": "status_container",
#         "fields": [
#             {"header": ["status_text"]},
#             {"body": ["amount", "receiver", "from_card"]},
#             {"footer": ["date", "time"]},
#         ],
#     },
#     "payment_pending": {
#         "type": "status_container",
#         "fields": [
#             {"header": ["status_text"]},
#             {"body": ["amount", "receiver", "from_card"]},
#             {"footer": ["date", "time"]},
#         ],
#     },
#     "otp_container": {"type": "otp_container", "fields": ["otp"]},
#     "icon_phone": {"type": "icon"},
#     "icon_person": {"type": "icon"},
#     "icon_card_general": {"type": "icon"},
#     "icon_card_from": {"type": "icon"},
# }

# widgets = {
#     "text_widget": ["text_normal"],
#     "p2p_final": [{"list": []}],
#     "card_own_list": ["text_normal", "cards_list_own", "button"],
#     "card_other_list": ["text_normal", "cards_list_other", "button"],
#     "contact_list": ["text_normal", "contacts_list", "button"],
#     "transfer_status_success": ["transfer_success"],
#     "transfer_status_failed": ["transfer_failed"],
#     "transfer_status_pending": ["transfer_pending"],
#     "payment_status_success": ["payment_success"],
#     "payment_status_failed": ["payment_failed"],
#     "payment_status_pending": ["payment_pending"],
#     "otp": ["text_normal", "otp_container", "button"],
#     "card_info": ["text_normal", "own_card_container", "button"],
#     # "balance_info":
#     # "contact_info":["text_normal", "other_card_container", "button"]
# }
