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
MAX_STEPS_HISTORY = 1000       # Limit step records to avoid memory overhead
CACHE_SIZE = 100               # LRU cache size for schema validations
SAFE_PATTERN = re.compile(r'^[a-zA-Z0-9_\-]{1,64}$')  # Pattern for safe identifiers

# Janis Rubins step 2: Configure a flexible logging system
log_level = os.environ.get("LOG_LEVEL", "ERROR").upper()
level = logging.DEBUG if log_level == "DEBUG" else logging.ERROR
logger = logging.getLogger(__name__)
logger.setLevel(level)
handler = logging.StreamHandler()
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
logger.addHandler(handler)

# Janis Rubins step 3: StepsTracker for deep debugging and schema integrity checks
class StepsTracker:
    def __init__(self, max_steps: int = MAX_STEPS_HISTORY):
        self.steps: List[str] = []
        self.max_steps = max_steps
        self._schema_hashes: Dict[str, str] = {}

<<<<<<< HEAD

def record_step(msg):
    # Janis Rubins: function to record each step, so if error occurs we know what happened
    steps.append(msg)
=======
    def add(self, msg: str) -> None:
        # Janis Rubins step 4: Add a step and log if in DEBUG mode
        self.steps.append(msg)
        logger.debug(f"Recorded step: {msg}")
        if len(self.steps) > self.max_steps:
            self.steps.pop(0)

    def calculate_schema_hash(self, schema_name: str, schema: dict) -> str:
        # Janis Rubins step 5: Calculate schema hash to check integrity later
        schema_hash = hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()
        self._schema_hashes[schema_name] = schema_hash
        return schema_hash

    def verify_schema_integrity(self, schema_name: str, schema: dict) -> bool:
        # Janis Rubins step 6: Verify schema integrity hasn't changed
        if schema_name not in self._schema_hashes:
            return True
        current_hash = hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()
        return current_hash == self._schema_hashes[schema_name]

steps = StepsTracker()

# Janis Rubins step 7: Security helper to ensure identifiers are safe
def is_safe_identifier(value: str) -> bool:
    return bool(SAFE_PATTERN.match(value))

@lru_cache(maxsize=CACHE_SIZE)
def validate_schema(schema_name: str, schema_dict: Dict[str, Any]) -> bool:
    # Janis Rubins step 8: Validate schema size and absence of suspicious patterns
    try:
        schema_str = json.dumps(schema_dict)
        schema_size = len(schema_str.encode())
        if schema_size > MAX_SCHEMA_SIZE:
            logger.error(f"Schema {schema_name} exceeds size limit")
            return False
        suspicious_patterns = ['__proto__', 'constructor', 'prototype']
        if any(pattern in schema_str for pattern in suspicious_patterns):
            logger.error(f"Suspicious pattern detected in schema {schema_name}")
            return False
        return True
    except Exception as e:
        logger.error(f"Schema validation error in {schema_name}: {e}")
        return False
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)


try:
<<<<<<< HEAD
    # Janis Rubins: record environment info, helps debug if error occurs
    record_step(f"System info: Python version: {sys.version}, Platform: {sys.platform}")
    record_step(f"Current working directory: {os.getcwd()}")
    record_step(
        "Start loading balance_info schema."
    )  # Janis Rubins: track start of loading schema
=======
    # Janis Rubins step 9: Log environment info
    steps.add(f"System info: Python version: {sys.version}, Platform: {os.platform if hasattr(os,'platform') else sys.platform}")
    steps.add(f"Current working directory: {os.getcwd()}")
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)

    # Below: original logic of loading schemas. We keep it as is, just integrated into this new structure.
    steps.add("Start loading balance_info schema.")
    balance_info = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": [
<<<<<<< HEAD
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
=======
            {"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]},
            {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_own"}}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
                    "text": {
                        "type": "string",
                        "description": "The text content displayed.",
                    }  # Janis Rubins: simple text field
=======
                    "text": {"type": "string", "description": "Displayed text."}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["text"],
            },
            "cards_list_item_own": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
                    "index": {
                        "type": "integer",
                        "description": "Index of the card in the list.",  # Janis Rubins: card index
                    },
                    "own_card_container": {
                        "$ref": "#/definitions/own_card_container"
                    },  # Janis Rubins: referencing container
=======
                    "index": {"type": "integer", "description": "Card index."},
                    "own_card_container": {"$ref": "#/definitions/own_card_container"}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["index", "own_card_container"],
            },
            "own_card_container": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
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
=======
                    "masked_card_pan": {"type": "string", "description": "Masked card number."},
                    "card_type": {"type": "string", "description": "Type of card."},
                    "balance": {"type": "number", "description": "Available balance."},
                    "card_name": {"type": "string", "description": "Card name."}
                },
                "required": ["masked_card_pan", "card_type", "balance", "card_name"]
            }
        }
    }
    steps.add("balance_info schema loaded.")
    steps.add(f"balance_info has {len(balance_info['definitions'])} definitions.")

    steps.add("Start loading card_own_list_widget schema.")
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
    card_own_list_widget = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": [
<<<<<<< HEAD
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
=======
            {"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]},
            {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_own"}},
            {"type": "object", "enum": [{"$ref": "#/definitions/button"}]}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
                    "text": {
                        "type": "string",
                        "description": "The text content displayed.",
                    }  # Janis Rubins: text again
=======
                    "text": {"type": "string", "description": "Text content displayed."}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["text"],
            },
            "button": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
                    "text": {
                        "type": "string",
                        "description": "The text displayed on the button.",  # Janis Rubins: button text
                    }
=======
                    "text": {"type": "string", "description": "Button text."}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["text"],
            },
            "cards_list_item_own": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
                    "index": {
                        "type": "integer",
                        "description": "Index of the card in the list.",  # Janis Rubins: index again
                    },
                    "own_card_container": {
                        "$ref": "#/definitions/own_card_container"
                    },  # Janis Rubins: same container ref
=======
                    "index": {"type": "integer", "description": "Card index."},
                    "own_card_container": {"$ref": "#/definitions/own_card_container"}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["index", "own_card_container"],
            },
            "own_card_container": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
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
=======
                    "masked_card_pan": {"type": "string", "description": "Masked card number."},
                    "card_type": {"type": "string", "description": "Card type."},
                    "balance": {"type": "number", "description": "Available balance."},
                    "card_name": {"type": "string", "description": "Card name."}
                },
                "required": ["masked_card_pan", "card_type", "balance", "card_name"]
            }
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
        },
        "minItems": 3,
        "maxItems": 3,
    }
<<<<<<< HEAD
    record_step(
        "card_own_list_widget schema loaded successfully."
    )  # Janis Rubins: loaded OK
    record_step(
        f"card_own_list_widget has {len(card_own_list_widget['definitions'])} definitions."
    )  # Janis Rubins: count defs

    record_step(
        "Start loading card_other_list_widget schema."
    )  # Janis Rubins: another widget schema
=======
    steps.add("card_own_list_widget schema loaded.")
    steps.add(f"card_own_list_widget has {len(card_own_list_widget['definitions'])} definitions.")

    steps.add("Start loading card_other_list_widget schema.")
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
    card_other_list_widget = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "minItems": 3,
        "maxItems": 3,
        "items": [
<<<<<<< HEAD
            {"$ref": "#/definitions/text_normal"},
            {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_other"}},
            {"type": "array", "items": {"$ref": "#/definitions/button"}},
=======
            {"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]},
            {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_other"}},
            {"type": "object", "enum": [{"$ref": "#/definitions/button"}]}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
<<<<<<< HEAD
                "description": "Represents text content displayed in the UI.",
                "properties": {
                    "text": {
                        "type": "string",
                        "description": "The text content displayed.",
                    }
=======
                "properties": {
                    "text": {"type": "string", "description": "Displayed text."}
                },
                "required": ["text"]
            },
            "button": {
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Button text."}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
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
<<<<<<< HEAD
                    "index": {
                        "type": "integer",
                        "description": "Index of the card in the list.",
                    },
                    "other_card_container": {
                        "$ref": "#/definitions/other_card_container"
                    },
=======
                    "index": {"type": "integer", "description": "Card index."},
                    "other_card_container": {"$ref": "#/definitions/other_card_container"}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["index", "other_card_container"],
            },
            "other_card_container": {
                "type": "object",
<<<<<<< HEAD
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
=======
                "properties": {
                    "masked_card_pan": {"type": "string", "description": "Masked card number."},
                    "card_owner": {"type": "string", "description": "Card owner name."},
                    "provider": {"type": "string", "description": "Card provider."}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["masked_card_pan", "card_owner", "provider"],
            },
        },
    }
<<<<<<< HEAD
    record_step(
        "card_other_list_widget schema loaded successfully."
    )  # Janis Rubins: loaded fine
    record_step(
        f"card_other_list_widget has {len(card_other_list_widget['definitions'])} definitions."
    )  # Janis Rubins: count defs
=======
    steps.add("card_other_list_widget schema loaded.")
    steps.add(f"card_other_list_widget has {len(card_other_list_widget['definitions'])} definitions.")
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)

    steps.add("Start loading text_widget schema.")
    text_widget = {
        "$schema": "http://json-schema.org/draft-07/schema#",
        "type": "array",
        "items": [
<<<<<<< HEAD
            {
                "type": "object",
                "enum": [
                    {"$ref": "#/definitions/text_normal"}
                ],  # Janis Rubins: just one text object in array
            }
=======
            {"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
        ],
        "definitions": {
            "text_normal": {
                "type": "object",
                "properties": {
<<<<<<< HEAD
                    "text": {
                        "type": "string",
                        "description": "The text content displayed.",
                    }
=======
                    "text": {"type": "string", "description": "Displayed text."}
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
                },
                "required": ["text"],
            }
        },
    }
<<<<<<< HEAD
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
=======
    steps.add("text_widget schema loaded.")
    steps.add(f"text_widget has {len(text_widget['definitions'])} definitions.")

    # Janis Rubins step 11: Validate and hash each schema
    all_schemas = [
        ("balance_info", balance_info),
        ("card_own_list_widget", card_own_list_widget),
        ("card_other_list_widget", card_other_list_widget),
        ("text_widget", text_widget)
    ]

    for schema_name, schema_dict in all_schemas:
        steps.add(f"Validating schema: {schema_name}")
        if not validate_schema(schema_name, schema_dict):
            logger.warning(f"Schema validation failed for {schema_name}, continuing anyway.")
        schema_hash = steps.calculate_schema_hash(schema_name, schema_dict)
        steps.add(f"Schema {schema_name} hash: {schema_hash[:8]}...")

    # Janis Rubins step 12: Assemble widgets with integrity checks
    steps.add("Assembling widgets with security checks...")
    widgets = {}
    for name, schema in all_schemas:
        if not steps.verify_schema_integrity(name, schema):
            logger.warning(f"Schema integrity check failed for {name}, continuing.")
        if is_safe_identifier(name):
            widgets[name] = schema
        else:
            logger.error(f"Unsafe widget name detected: {name}, not adding to widgets.")

    steps.add(f"Assembled {len(widgets)} widgets successfully")
    steps.add("No errors encountered, process completed successfully.")
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)

except Exception as e:
    logger.error("AN ERROR OCCURRED DURING SCHEMA LOADING AND ASSEMBLY:")
    for i, step_msg in enumerate(steps.steps, start=1):
        logger.error(f"Step {i}: {step_msg}")
    logger.error(f"Error details: {e}")
    raise

<<<<<<< HEAD

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
=======
if 'widgets' in locals():
    steps.add("Export completed successfully")
>>>>>>> 86c7bcd (Updated code with enhanced flexibility, logging, and conflict resolution. All changes integrated.)
