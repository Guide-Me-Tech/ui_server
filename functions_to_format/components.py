balance_info = {
    "$schema": "",
    "type": "array",
    "items": [
        {"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]},
        {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_own"}},
    ],
    "definitions": {
        "text_normal": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text content displayed."}
            },
            "required": ["text"],
        },
        "cards_list_item_own": {
            "type": "object",
            "properties": {
                "index": {
                    "type": "integer",
                    "description": "Index of the card in the list.",
                },
                "own_card_container": {"$ref": "#definitions/own_card_container"},
            },
            "required": ["index", "own_card_container"],
            "definitions": {
                "own_card_container": {
                    "type": "object",
                    "properties": {
                        "masked_card_pan": {
                            "type": "string",
                            "description": "Masked card number (e.g., **** 1234).",
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
                    "required": [
                        "masked_card_pan",
                        "card_type",
                        "balance",
                        "card_name",
                    ],
                }
            },
        },
    },
}


card_own_list_widget = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": [
        {"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]},
        {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_own"}},
        {"type": "object", "enum": [{"$ref": "#/definitions/button"}]},
    ],
    "definitions": {
        "text_normal": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text content displayed."}
            },
            "required": ["text"],
        },
        "button": {
            "type": "object",
            "properties": {
                "text": {
                    "type": "string",
                    "description": "The text displayed on the button.",
                }
            },
            "required": ["text"],
        },
        "cards_list_item_own": {
            "type": "object",
            "properties": {
                "index": {
                    "type": "integer",
                    "description": "Index of the card in the list.",
                },
                "own_card_container": {"$ref": "#/own_card_container"},
            },
            "required": ["index", "own_card_container"],
            "definitions": {
                "own_card_container": {
                    "type": "object",
                    "properties": {
                        "masked_card_pan": {
                            "type": "string",
                            "description": "Masked card number (e.g., **** 1234).",
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
                    "required": [
                        "masked_card_pan",
                        "card_type",
                        "balance",
                        "card_name",
                    ],
                }
            },
        },
    },
    "minItems": 3,
    "maxItems": 3,
}


card_other_list_widget = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": [
        {"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]},
        {"type": "array", "items": {"$ref": "#/definitions/cards_list_item_other"}},
        {"type": "object", "enum": [{"$ref": "#/definitions/button"}]},
    ],
    "definitions": {
        "text_normal": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text content displayed."}
            },
            "required": ["text"],
        },
        "button": {
            "type": "object",
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
            "properties": {
                "index": {
                    "type": "integer",
                    "description": "Index of the card in the list.",
                },
                "other_card_container": {"$ref": "#/OtherCardContainer"},
            },
            "required": ["index", "other_card_container"],
        },
        "definitions": {
            "other_card_container": {
                "type": "object",
                "description": "container which has information about the card of other people",
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
                        "description": "The provider of the card.",
                    },
                },
                "required": ["masked_card_pan", "card_owner", "provider"],
            }
        },
    },
    "minItems": 3,
    "maxItems": 3,
}

text_widget = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": [{"type": "object", "enum": [{"$ref": "#/definitions/text_normal"}]}],
    "definitions": {
        "text_normal": {
            "type": "object",
            "properties": {
                "text": {"type": "string", "description": "The text content displayed."}
            },
            "required": ["text"],
        },
    },
}


widgets = {
    "balance_info": balance_info,
    "card_own_list_widget": card_own_list_widget,
    "card_other_list_widget": card_other_list_widget,
    "text_widget": text_widget,
}


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
