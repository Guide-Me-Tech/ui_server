import os
import sys
import logging
from .base_adapter import BaseAdapter

"""
Why this code is needed:
- Provides a fallback adapter that returns a minimal UI if no others match.
- Ensures system always returns a safe default response.
- Flexible: If needed, the minimal UI could be customized via environment variables.

Environment Variables:
- ADAPTER_LOG_LEVEL: Controls fallback adapter logging detail.

Deep logging ensures easy debugging if fallback is chosen unexpectedly.
"""

# Janis Rubins step 1: Load ADAPTER_LOG_LEVEL again to ensure consistent logging.
ADAPTER_LOG_LEVEL = os.environ.get("ADAPTER_LOG_LEVEL", "ERROR").upper()

# Janis Rubins step 2: Set up logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(ADAPTER_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

class FallbackAdapter(BaseAdapter):
    """
    Janis Rubins step 3: FallbackAdapter class.
    match() returns False, ensuring it's only chosen if no others match.
    adapt() returns minimal UI.
    """

    def match(self, data: dict) -> bool:
        self.log_match_attempt(data)
        # Janis Rubins step 4: Always return False so it's chosen last.
        return False

    def adapt(self, data: dict) -> dict:
        self.log_adapt_start(data)
        # Janis Rubins step 5: Minimal UI, could be made configurable if needed.
        minimal_ui = {
            "type": "fallback",
            "message": "Data format not recognized. Minimal UI displayed."
        }
        logger.debug("FallbackAdapter: returning minimal UI.")
        return minimal_ui
