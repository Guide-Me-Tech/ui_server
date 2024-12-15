import os
import sys
import logging
from ..base_adapter import BaseAdapter

"""
Why this code is needed:
- Another known adapter handling a different format (e.g., XML-like).
- Uses environment variables to define match criteria.
- Logs each step for debugging.
- Adaptation might, for example, pull "items" list from data and present as a UI list.

Environment variables:
- KNOWN_TWO_MATCH_KEY: The key to check in data to identify this format (default: "type")
- KNOWN_TWO_MATCH_VALUE: The expected value (default: "xml")

If data[type] == "xml", we match and adapt accordingly.
"""

# Janis Rubins step 1: Load logging level
ADAPTER_LOG_LEVEL = os.environ.get("ADAPTER_LOG_LEVEL", "ERROR").upper()

# Janis Rubins step 2: Setup logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(ADAPTER_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

class KnownAdapterTwo(BaseAdapter):
    def __init__(self):
        super().__init__()
        # Janis Rubins step 3: ENV-based config
        self.match_key = os.environ.get("KNOWN_TWO_MATCH_KEY", "type")
        self.match_value = os.environ.get("KNOWN_TWO_MATCH_VALUE", "xml")

    def match(self, data: dict) -> bool:
        self.log_match_attempt(data)
        # Janis Rubins step 4: Simple check for match_key/value
        if data.get(self.match_key) == self.match_value:
            logger.debug(f"KnownAdapterTwo matched data using {self.match_key}={self.match_value}.")
            return True
        return False

    def adapt(self, data: dict) -> dict:
        self.log_adapt_start(data)
        # Janis Rubins step 5: Construct UI
        # Suppose data has "items" as a list of structures we turn into UI cards
        items = data.get("items", [])
        ui_items = [{"text": str(i)} for i in items]
        adapted_ui = {
            "type": "known_format_two",
            "items": ui_items
        }
        logger.debug("KnownAdapterTwo adapted data into UI items.")
        return adapted_ui
