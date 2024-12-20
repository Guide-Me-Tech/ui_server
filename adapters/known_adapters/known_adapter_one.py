import os
import sys
import logging
from ..base_adapter import BaseAdapter

"""
Why this code is needed:
- Demonstrates a known adapter that handles a specific data format (e.g., JSON-like).
- Uses environment variables to configure matching criteria and keys.
- Deep logging to understand each step of matching and adaptation.
- Minimal overhead: simple key checks, no heavy parsing until matched.

Environment variables:
- KNOWN_ONE_FORMAT_KEY: The data key name to check (default: "format")
- KNOWN_ONE_FORMAT_VALUE: The expected value to match this adapter (default: "json")

If data[format_key] == format_value, adapter matches.
Then adapt() transforms data into a structured UI format.
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

class KnownAdapterOne(BaseAdapter):
    def __init__(self):
        super().__init__()
        # Janis Rubins step 3: Load config from ENV
        self.format_key = os.environ.get("KNOWN_ONE_FORMAT_KEY", "format")
        self.format_value = os.environ.get("KNOWN_ONE_FORMAT_VALUE", "json")

    def match(self, data: dict) -> bool:
        self.log_match_attempt(data)
        # Janis Rubins step 4: Minimal overhead matching
        # Check if data has the key and value matches expected format
        if data.get(self.format_key) == self.format_value:
            logger.debug(f"KnownAdapterOne matched data using {self.format_key}={self.format_value}.")
            return True
        return False

    def adapt(self, data: dict) -> dict:
        self.log_adapt_start(data)
        # Janis Rubins step 5: Adapt data to a standardized UI
        # Example: extracting "title" and "content" keys for UI
        title = data.get("title", "No Title")
        content = data.get("content", {})
        adapted_ui = {
            "type": "known_format_one",
            "title": title,
            "content": content
        }
        logger.debug("KnownAdapterOne adapted data successfully.")
        return adapted_ui
