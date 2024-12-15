import os
import sys
import logging
from ..base_adapter import BaseAdapter

"""
Why this code is needed:
- Another known adapter for a proprietary JSON schema.
- Uses ENV to define match criteria.
- Suppose we match if data["schema_version"]="v2" and data["kind"]="custom".
- Adaptation might extract "records" and display them as UI cards.

Environment variables:
- KNOWN_SIX_SCHEMA_KEY: key for schema version (default: "schema_version")
- KNOWN_SIX_SCHEMA_VALUE: expected version (default: "v2")
- KNOWN_SIX_KIND_KEY: key for kind (default: "kind")
- KNOWN_SIX_KIND_VALUE: expected kind (default: "custom")

If both conditions met, we match.
Adaptation: transforms records into UI cards.
"""

# Janis Rubins step 1: Load log level
ADAPTER_LOG_LEVEL = os.environ.get("ADAPTER_LOG_LEVEL", "ERROR").upper()

# Janis Rubins step 2: Logging setup
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(ADAPTER_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

class KnownAdapterSix(BaseAdapter):
    def __init__(self):
        super().__init__()
        # Janis Rubins step 3: ENV config
        self.schema_key = os.environ.get("KNOWN_SIX_SCHEMA_KEY", "schema_version")
        self.schema_val = os.environ.get("KNOWN_SIX_SCHEMA_VALUE", "v2")
        self.kind_key = os.environ.get("KNOWN_SIX_KIND_KEY", "kind")
        self.kind_val = os.environ.get("KNOWN_SIX_KIND_VALUE", "custom")

    def match(self, data: dict) -> bool:
        self.log_match_attempt(data)
        # Janis Rubins step 4: Check both conditions
        if data.get(self.schema_key) == self.schema_val and data.get(self.kind_key) == self.kind_val:
            logger.debug(f"KnownAdapterSix matched with {self.schema_key}={self.schema_val} and {self.kind_key}={self.kind_val}.")
            return True
        return False

    def adapt(self, data: dict) -> dict:
        self.log_adapt_start(data)
        # Janis Rubins step 5: Suppose data["records"] is a list of dicts
        records = data.get("records", [])
        ui_cards = []
        for rec in records:
            # Create a simple UI card from record data
            title = rec.get("title", "No Title")
            description = rec.get("description", "")
            ui_cards.append({
                "type": "card",
                "title": title,
                "description": description
            })

        adapted = {
            "type": "known_format_six",
            "cards": ui_cards
        }
        logger.debug("KnownAdapterSix adapted records into UI cards.")
        return adapted
