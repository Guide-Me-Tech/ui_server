import os
import sys
import logging
from ..base_adapter import BaseAdapter

"""
Why this code is needed:
- Handles a "binary-like" format scenario.
- Maybe data contains a binary blob in base64.
- We use ENV to decide which key to check and value.

Environment variables:
- KNOWN_FIVE_KEY: key (default: "data_type")
- KNOWN_FIVE_VALUE: expected value (default: "binary")

If data[data_type]="binary", match.
Adaptation: converts binary data into a UI-friendly hex string or summary.
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

import base64

class KnownAdapterFive(BaseAdapter):
    def __init__(self):
        super().__init__()
        # Janis Rubins step 3: ENV config
        self.match_key = os.environ.get("KNOWN_FIVE_KEY", "data_type")
        self.match_value = os.environ.get("KNOWN_FIVE_VALUE", "binary")

    def match(self, data: dict) -> bool:
        self.log_match_attempt(data)
        if data.get(self.match_key) == self.match_value:
            logger.debug(f"KnownAdapterFive matched with {self.match_key}={self.match_value}.")
            return True
        return False

    def adapt(self, data: dict) -> dict:
        self.log_adapt_start(data)
        # Janis Rubins step 5: Suppose data["binary_data"] is a base64 string
        b64_str = data.get("binary_data", "")
        try:
            raw_bytes = base64.b64decode(b64_str)
            # Represent as hex for UI
            hex_str = raw_bytes.hex()
            adapted = {
                "type": "known_format_five",
                "hex_representation": hex_str[:64] + "..." if len(hex_str) > 64 else hex_str
            }
            logger.debug("KnownAdapterFive adapted binary data to hex representation.")
            return adapted
        except Exception as e:
            logger.error(f"Error decoding binary data: {e}", exc_info=True)
            # Return minimal fallback inside adapter if needed
            return {"type": "known_format_five", "error": "Invalid binary data"}
