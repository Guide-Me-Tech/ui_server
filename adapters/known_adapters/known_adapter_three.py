import os
import sys
import logging
from ..base_adapter import BaseAdapter

"""
Why this code is needed:
- A third known adapter for another format (e.g., CSV-like).
- ENV variables control how it matches (maybe a special "source" key).
- Logs steps for transparency.
- Minimal overhead: only parse/convert if matched.

Environment variables:
- KNOWN_THREE_SOURCE_KEY: key to check (default: "source")
- KNOWN_THREE_SOURCE_VALUE: expected value (default: "csv")

If data[source]="csv", we match and adapt.
Adaptation might transform CSV-like data (a simple array of arrays) into UI tables.
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

class KnownAdapterThree(BaseAdapter):
    def __init__(self):
        super().__init__()
        # Janis Rubins step 3: ENV-based config
        self.source_key = os.environ.get("KNOWN_THREE_SOURCE_KEY", "source")
        self.source_value = os.environ.get("KNOWN_THREE_SOURCE_VALUE", "csv")

    def match(self, data: dict) -> bool:
        self.log_match_attempt(data)
        # Janis Rubins step 4: Check source key
        if data.get(self.source_key) == self.source_value:
            logger.debug(f"KnownAdapterThree matched data using {self.source_key}={self.source_value}.")
            return True
        return False

    def adapt(self, data: dict) -> dict:
        self.log_adapt_start(data)
        # Janis Rubins step 5: Suppose data['rows'] is a list of lists representing CSV rows
        rows = data.get("rows", [])
        # Convert them into a table UI structure
        table = {
            "type": "known_format_three",
            "table": {
                "headers": rows[0] if rows else [],
                "data": rows[1:] if len(rows) > 1 else []
            }
        }
        logger.debug("KnownAdapterThree adapted CSV-like data into a table UI.")
        return table
