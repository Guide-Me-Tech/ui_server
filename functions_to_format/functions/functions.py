import jsonschema
import jsonschema.exceptions
import json
import re
import hashlib
from functools import lru_cache
from typing import Any, Dict
from conf import logger
from .general import (
    add_ui_to_widget,
    Widget,
    TextWidget,
    ButtonsWidget,
    build_buttons_row,
    build_text_widget,
    WidgetInput,
)
import pydivkit as dv
from models.build import BuildOutput
from pydantic import BaseModel


def chatbot_answer(llm_output: str, backend_output, version="v2") -> BuildOutput:
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data

    text_widget = TextWidget(
        order=1,
        values=[{"text": llm_output}],
    )

    widgets = add_ui_to_widget(
        {
            build_text_widget: WidgetInput(
                widget=text_widget,
                args={"text": llm_output},
            ),
        },
        version,
    )

    return BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


def unauthorized_response(llm_output, backend_output, version="v2"):
    # Janis Rubins: logic unchanged, just returns text_widget schema and llm_output as data
    return {
        "data": llm_output,
    }


class Contact(BaseModel):
    first_name: str
    last_name: str
    phone: str


def build_contacts_list_widget(contacts: list[Contact]) -> list[dict]:
    items = [
        dv.DivText(
            text="Contacts List",
            font_family="Manrope",
            font_size=18,
            font_weight=dv.DivFontWeight.BOLD,
            text_color="#111133",
            margins=dv.DivEdgeInsets(bottom=16),
        )
    ]

    for contact in contacts:
        send_action = dv.DivAction(
            log_id=f"send_contact_{contact.phone}",
            url="divkit://send_contact",
            payload={
                "first_name": contact.first_name,
                "last_name": contact.last_name,
                "phone": contact.phone,
            },
        )

        contact_cell = dv.DivContainer(
            orientation="vertical",
            paddings=dv.DivEdgeInsets(left=16, right=16, top=8, bottom=8),
            border=dv.DivBorder(
                stroke=dv.DivStroke(color="#E0E0E0"),
            ),
            items=[
                dv.DivText(
                    text=f"{contact.first_name} {contact.last_name}",
                    font_family="Manrope",
                    font_size=16,
                    font_weight=dv.DivFontWeight.MEDIUM,
                    text_color="#111133",
                    line_height=20,
                    letter_spacing=0,
                ),
                dv.DivText(
                    text=contact.phone,
                    font_family="Manrope",
                    font_size=14,
                    font_weight=dv.DivFontWeight.REGULAR,
                    text_color="#808080",
                    line_height=20,
                    letter_spacing=0,
                ),
            ],
            action=send_action,
        )
        items.append(contact_cell)

    container = dv.DivContainer(
        orientation="vertical",
        # spacing=8,
        items=items,
    )
    container = dv.make_div(container)
    with open("contacts.json", "w") as f:
        json.dump(container, f, indent=4)
    return container


def build_contacts_list(llm_output: str, backend_output, version="v2") -> list[dict]:
    contacts_list: list[dict] = []

    contact_widget = Widget(
        order=1,
        name="contacts_list",
        type="contacts_list",
        layout="horizontal",
        fields=["contacts"],
        values=[{"contacts": contacts_list}],
    )
    # text_widget = TextWidget(
    #     order=1,
    #     values=[{"text": llm_output}],
    # )
    buttons = ButtonsWidget(
        order=2,
        values=[{"text": "cancel"}],
    )

    for contact in backend_output:
        contacts_list.append(
            Contact(
                first_name=contact["first_name"],
                last_name=contact["last_name"],
                phone=contact["phone"],
            )
        )

    widgets = add_ui_to_widget(
        {
            build_contacts_list_widget: WidgetInput(
                widget=contact_widget,
                args={
                    "contacts": contacts_list,
                },
            ),
            build_buttons_row: WidgetInput(
                widget=buttons,
                args={"button_texts": ["cancel"]},
            ),
            # build_text_widget: WidgetInput(
            #     widget=text_widget,
            #     args={"text": llm_output},
            # ),
        },
        version,
    )

    return BuildOutput(
        widgets_count=1,
        widgets=[widget.model_dump(exclude_none=True) for widget in widgets],
    )


########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
########################################################
######### LEGACY UNUSED CODE #########
# Janis Rubins: precompile validator to avoid repeated schema parsing

# Janis Rubins step 1: Security and Performance Constants
MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB limit for input/data size
CACHE_SIZE = 100  # LRU cache size for schema validations
SAFE_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")  # Pattern for safe identifiers
SUSPICIOUS_PATTERNS = ["__proto__", "constructor", "prototype", "<script"]


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
