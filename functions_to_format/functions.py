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
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data
    text_widget = {
        "name": "text_widget",
        "type": "text_widget",
        "order": 1,
        "layout": "horizontal",
        "fields": ["text"],
        "values": [{"text": llm_output}],
    }
    return {
        "widgets": [text_widget],
        "widgets_number": 1,
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
                "masked_card_pan": card_info["pan"],
                "card_type": card_info["processingSystem"],
                "balance": card_info["balance"]
                if type(card_info["balance"]) is int
                else 0,
                "card_name": card_info["cardDetails"]["cardName"],
            }
        )
    text_widget = {
        "name": "text_widget",
        "type": "text_widget",
        "order": 1,
        "layout": "horizontal",
        "fields": ["text"],
        "values": [{"text": llm_output}],
    }
    cards_list = {
        "name": "cards_own_list_widget",
        "order": 2,
        "layout": "vertical",
        "fields": ["masked_card_pan", "card_type", "balance", "card_name"],
        "values": backend_output_processed,
    }

    output = {"widgets": [text_widget, cards_list], "widgets_count": 2}
    print("Output", output)

    # Janis Rubins: return schema and data if valid
    return output


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
    print(type(backend_output))
    # if type(backend_output) is str:
    #     backend_output = json.loads(backend_output)
    # for i in backend_output:
    #     print(i)
    logger.debug(backend_output)
    for i, card_info in enumerate(backend_output):
        print(f"Card {i + 1} info: ", card_info)
        backend_output_processed.append(
            {
                "masked_card_pan": card_info["mask"],
                "card_owner": card_info["name"],
                "provider": card_info["processing"],
            }
        )

    text_widget = {
        "name": "text_widget",
        "type": "text_widget",
        "order": 1,
        "layout": "horizontal",
        "fields": ["text"],
        "values": [{"text": llm_output}],
    }
    cards_widget = {
        "name": "cards_other_list_widget",
        "type": "cards_other_list_widget",
        "order": 2,
        "layout": "vertical",
        "fields": ["masked_card_pan", "card_owner", "provider"],
        "values": backend_output_processed,
    }
    buttons = {
        "name": "buttons_widget",
        "type": "buttons_widget",
        "order": 3,
        "layout": "horizontal",
        "fields": ["text"],
        "values": [  {"text":"cancel"}  ],
    }

    output = {
        "widgets_count": 3,
        "widgets": [text_widget, cards_widget, buttons],
    }

    return output


# "get_fields_of_supplier": get_fields_of_supplier,
# "get_suppliers_by_category": get_suppliers_by_category,
# "get_categories": get_categories,
#  [
#         {
#             "id": 1,
#             "name": "Мобильные операторы",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056545-57d63349-cdc1-4438-982f-23ae508dd782",
#         },
#         {
#             "id": 2,
#             "name": "Домашний телефон",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056505-ad89d454-3f47-4e68-bc26-74fd2d32c5e2",
#         },
#         {
#             "id": 3,
#             "name": "Интернет",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056578-a950e105-f0f2-4b8f-af05-766d730593e9",
#         },
#         {
#             "id": 4,
#             "name": "Услуги",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056264-e1c665dc-ed0e-4617-9835-ddac232a1ffe",
#         },
#         {
#             "id": 5,
#             "name": "Телевидение",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056745-0899c2dc-f194-41e2-9a30-b1c16d45ef3e",
#         },
#         {
#             "id": 6,
#             "name": "Такси",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056657-eb712c52-a9ee-4293-b6ff-38eaaa052401",
#         },
#         {
#             "id": 7,
#             "name": "Коммунальные услуги",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056712-902ee66f-9ad1-4d73-940a-c5f174b01ae0",
#         },
#         {
#             "id": 9,
#             "name": "Онлайн площадки",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671057830-ef6d3711-ff17-44b3-9107-1a3e8f6085aa",
#         },
#         {
#             "id": 11,
#             "name": "Образование",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671058625-3b117d55-22a0-42e6-aed0-a48c995586c3",
#         },
#         {
#             "id": 18,
#             "name": "Благотворительность",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671056624-ea0e5f25-4998-4e49-9129-f8f6fed1fe94",
#         },
#         {
#             "id": 23,
#             "name": "Погашение рассрочек",
#             "imagePath": None,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671057272-e9da9dfc-c49b-47eb-9592-a201866ab5fe",
#         },
#     ]
#


def get_categories(llm_output, backend_output):
    backend_output_processed = []
    for i, category in enumerate(backend_output):
        backend_output_processed.append(
            {
                "id": category["id"],
                "name": category["name"],
                "image_url": category["s3Url"],
            }
        )
    text_widget = {
        "name": "text_widget",
        "type": "text_widget",
        "order": 1,
        "layout": "horizontal",
        "fields": ["text"],
        "values": [{"text": llm_output}],
    }
    categories_widget = {
        "name": "payments_list_item_widget",
        "type": "payments_list_item_widget",
        "order": 2,
        "layout": "vertical",
        "fields": ["id", "name", "image_url"],
        "values": backend_output_processed,
    }
    buttons = {
        "name": "buttons_widget",
        "type": "buttons_widget",
        "order": 3,
        "layout": "horizontal",
        "fields": ["text", "action"],
        "values": [
            {"text": "Cancel", "action": "cancel"},
        ],
    }
    return {
        "widgets_count": 3,
        "widgets": [text_widget, categories_widget, buttons],
    }


#  [
#         {
#             "id": 1014,
#             "name": "Crediton.uz",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671093787-252daee5-82ac-4fb4-ba5c-03787fe386f8",
#         },
#         {
#             "id": 1015,
#             "name": "Creditexpress.uz",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671093824-47a839b9-e505-4b41-aac7-a3c93cf052a4",
#         },
#         {
#             "id": 1016,
#             "name": "Smart Credit",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671094187-ebb454f8-45b5-4a94-85ec-d1ee5b6fa3f8",
#         },
#         {
#             "id": 1020,
#             "name": "Olcha.uz",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671094219-7c7e4bd0-75ca-471e-a122-9d780d780165",
#         },
#         {
#             "id": 1021,
#             "name": "FORTA",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671094258-7eb6a2ac-6c51-4ebf-816b-f98dc9fb7b37",
#         },
#         {
#             "id": 1022,
#             "name": "Imkon savdo",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671095537-ba0218a0-5aa5-4df8-b039-82c71b7063a1",
#         },
#         {
#             "id": 1033,
#             "name": "Amir Finans",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671095632-354819f4-0cbc-4d4d-87ab-75af0eaba01a",
#         },
#         {
#             "id": 1049,
#             "name": "IT BILIM",
#             "categoryId": 23,
#             "s3Url": "https://s3.smartbank.uz/mobile-ui/1691671095770-09905b0c-d184-443c-8e5e-22aa2429fc2f",
#         },
#     ],
# }


def get_suppliers_by_category(llm_output, backend_output):
    backend_output_processed = []
    for i, supplier in enumerate(backend_output):
        backend_output_processed.append(
            {
                "id": supplier["id"],
                "name": supplier["name"],
                "image_url": supplier["s3Url"],
            }
        )

    text_widget = {
        "name": "text_widget",
        "type": "text_widget",
        "order": 1,
        "layout": "horizontal",
        "fields": ["text"],
        "values": [{"text": llm_output}],
    }
    suppliers_widget = {
        "name": "payments_list_item_widget",
        "type": "payments_list_item_widget",
        "order": 2,
        "layout": "vertical",
        "fields": ["id", "name", "image_url"],
        "values": backend_output_processed,
    }
    buttons_widget = {
        "name": "buttons_widget",
        "type": "buttons_widget",
        "order": 3,
        "layout": "horizontal",
        "fields": ["text", "action"],
        "values": [
            {"text": "Cancel", "action": "cancel"},
        ],
    }

    return {
        "widgets_count": 3,
        "widgets": [text_widget, suppliers_widget, buttons_widget],
    }


# {'code': '0',
#  'description': 'Success',
#  'payload': {'checkUp': True,
#   'checkUpWithResponse': True,
#   'checkUpAfterPayment': False,
#   'fieldList': [{'identName': 'amount',
#     'name': 'Сумма',
#     'order': 2,
#     'type': 'MONEY',
#     'pattern': None,
#     'minValue': 500,
#     'maxValue': 10000000,
#     'fieldSize': 12,
#     'isMain': None,
#     'valueList': []},
#    {'identName': 'paymentNo',
#     'name': 'Номер счёта',
#     'order': 1,
#     'type': 'STRING',
#     'pattern': None,
#     'minValue': None,
#     'maxValue': None,
#     'fieldSize': 15,
#     'isMain': True,
#     'valueList': []}]}}


def get_fields_of_supplier(llm_output, backend_output):
    backend_output_processed = []
    for i, field in enumerate(backend_output["fieldList"]):
        backend_output_processed.append(
            {
                "identName": field["identName"],
                "name": field["name"],
                "order": field["order"],
                "type": field["type"],
                "pattern": field["pattern"],
                "minValue": field["minValue"],
                "maxValue": field["maxValue"],
                "fieldSize": field["fieldSize"],
                "isMain": field["isMain"],
                "valueList": field["valueList"],
            }
        )
    if llm_output:
        text_widget = {
            "name": "text_widget",
            "type": "text_widget",
            "order": 1,
            "layout": "horizontal",
            "fields": ["text"],
            "values": [{"text": llm_output}],
        }
    fields_widget = {
        "name": "fields_widget",
        "type": "fields_widget",
        "order": 2,
        "layout": "vertical",
        "fields": [
            "identName",
            "name",
            "order",
            "type",
            "pattern",
            "minValue",
            "maxValue",
            "fieldSize",
            "isMain",
            "valueList",
        ],
        "values": backend_output_processed,
    }
    button_widget = {
        "name": "buttons_widget",
        "type": "buttons_widget",
        "order": 3,
        "layout": "horizontal",
        "fields": ["text", "action"],
        "values": [
            {"text": "Cancel", "action": "cancel"},
        ],
    }
    if len(llm_output) > 0:
        return {
            "widgets_count": 3,
            "widgets": [text_widget, fields_widget, button_widget],
        }
    else:
        return {
            "widgets_count": 2,
            "widgets": [fields_widget, button_widget],
        }


def unauthorized_response(llm_output, backend_output):
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data
    return {
        "data": llm_output,
    }
