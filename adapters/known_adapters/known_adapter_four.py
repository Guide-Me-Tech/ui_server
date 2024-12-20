import os
import sys
import logging
from ..base_adapter import BaseAdapter

"""
Why this code is needed:
- Another known adapter handling a "YAML-like" format.
- Uses environment variables for matching key/value.
- Detailed logging and minimal overhead.

Environment variables:
- KNOWN_FOUR0_KEY: The key to check (default: "input_format")
- KNOWN_FOUR0_VALUE: The value expected (default: "yaml")

If data[input_format] == "yaml", we match.
Adaptation: Suppose we convert a "yaml" dict into a nested UI structure.
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

class KnownAdapterFour0(BaseAdapter):
    def __init__(self):
        super().__init__()
        # Janis Rubins step 3: Load config from ENV
        self.match_key = os.environ.get("KNOWN_FOUR0_KEY", "input_format")
        self.match_value = os.environ.get("KNOWN_FOUR0_VALUE", "yaml")

    def match(self, data: dict) -> bool:
        self.log_match_attempt(data)
        # Janis Rubins step 4: Check if data has expected key/value
        if data.get(self.match_key) == self.match_value:
            logger.debug(f"KnownAdapterFour0 matched with {self.match_key}={self.match_value}.")
            return True
        return False

    def adapt(self, data: dict) -> dict:
        self.log_adapt_start(data)
        # Janis Rubins step 5: Suppose "yaml" structure stored in data["structure"]
        structure = data.get("structure", {})
        adapted = {
            "type": "known_format_four0",
            "nested_structure": structure
        }
        logger.debug("KnownAdapterFour0 adapted YAML-like data into UI structure.")
        return adapted
