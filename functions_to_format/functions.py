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
import logging
import os
import re
import json
import hashlib
from functools import lru_cache
from typing import Any, Dict

# Janis Rubins step 1: Security and Performance Constants
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB limit for input/data size
CACHE_SIZE = 100  # LRU cache size for schema validations
SAFE_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")  # Pattern for safe identifiers
SUSPICIOUS_PATTERNS = ["__proto__", "constructor", "prototype", "<script"]

# Janis Rubins step 2: Set up a flexible logging system
log_level = os.environ.get("LOG_LEVEL", "ERROR").upper()
level = logging.DEBUG if log_level == "DEBUG" else logging.ERROR
logger = logging.getLogger(__name__)
logger.setLevel(level)
handler = logging.StreamHandler()
handler.setFormatter(
    logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s]: %(message)s")
)
logger.addHandler(handler)


def is_safe_identifier(value: str) -> bool:
    # Janis Rubins step 3: Ensure identifiers are safe to prevent malicious keys or names
    return bool(SAFE_PATTERN.match(value))


@lru_cache(maxsize=CACHE_SIZE)
def sanitize_output(data: Any) -> Any:
    # Janis Rubins step 4: Sanitize output data to prevent injection attacks
    # This does not break functionality, just adds a layer of security
    if isinstance(data, dict):
        return {
            k: sanitize_output(v) for k, v in data.items() if is_safe_identifier(str(k))
        }
    elif isinstance(data, list):
        return [sanitize_output(x) for x in data]
    elif isinstance(data, str):
        # Basic HTML/script sanitization
        return data.replace("<", "&lt;").replace(">", "&gt;")
    return data


class SchemaValidator:
    # Janis Rubins step 5: SchemaValidator class to handle validation and caching
    def __init__(self):
        self.validators = {}
        self._schema_hashes = {}

    def _calculate_hash(self, schema: Dict) -> str:
        # Janis Rubins step 6: Calculate schema hash for integrity checks
        return hashlib.sha256(json.dumps(schema, sort_keys=True).encode()).hexdigest()

    def prepare_validator(self, name: str, schema: Dict) -> None:
        # Janis Rubins step 7: Prepare and cache validator with integrity check
        try:
            schema_str = json.dumps(schema)
            if len(schema_str.encode()) > MAX_PAYLOAD_SIZE:
                logger.error(f"Schema {name} exceeds size limit")
                return

            schema_hash = self._calculate_hash(schema)
            if name in self._schema_hashes and self._schema_hashes[name] != schema_hash:
                logger.error(f"Schema {name} integrity check failed")
                return

            self.validators[name] = jsonschema.Draft7Validator(schema)
            self._schema_hashes[name] = schema_hash
            logger.debug(f"Validator prepared for {name}")
        except Exception as e:
            logger.error(f"Error preparing validator for {name}: {e}")

    @lru_cache(maxsize=CACHE_SIZE)
    def validate(self, name: str, data: Any) -> bool:
        # Janis Rubins step 8: Validate data against cached schema
        if name not in self.validators:
            logger.error(f"No validator found for {name}")
            return False

        data_str = json.dumps(data)
        if len(data_str.encode()) > MAX_PAYLOAD_SIZE:
            logger.error("Input data exceeds size limit")
            return False

        if any(pattern in data_str.lower() for pattern in SUSPICIOUS_PATTERNS):
            logger.error("Suspicious pattern detected in input")
            return False

        try:
            self.validators[name].validate(data)
            return True
        except Exception as e:
            logger.error(f"Validation error in {name}: {e}")
            return False


# Initialize schema validator and prepare validators if available
schema_validator = SchemaValidator()

if "balance_card" in widgets:
    schema_validator.prepare_validator("balance_card", widgets["balance_card"])

if "text_widget" in widgets:
    schema_validator.prepare_validator("text_widget", widgets["text_widget"])


def chatbot_answer(llm_output, backend_output):
    # Janis Rubins step 9: Returns text_widget schema and data
    # Sanitized and validated if possible
    logger.debug("chatbot_answer called")
    try:
        sanitized_output = sanitize_output(llm_output)
        if "text_widget" in widgets and schema_validator.validate(
            "text_widget", sanitized_output
        ):
            return {
                "schema": widgets["text_widget"],
                "data": sanitized_output,
            }
        else:
            logger.error(
                "text_widget validation failed or schema not found, returning None."
            )
            return None
    except Exception as e:
        logger.error(f"Error in chatbot_answer: {e}")
        return None


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
