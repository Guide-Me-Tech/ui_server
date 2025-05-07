import abc
import logging
import os
import sys

"""
Why this code is needed:
- Defines a standard interface (BaseAdapter) for data adapters.
- Ensures all adapters implement 'match' and 'adapt' methods, enabling a consistent approach.
- Encourages easy addition of new adapters, each potentially handling different data formats.
- Deep logging aids in debugging adapter selection issues.

Environment Variables:
- ADAPTER_LOG_LEVEL: Controls verbosity of adapter-related logs.
"""

# Janis Rubins step 1: Load environment variable for logging level
ADAPTER_LOG_LEVEL = os.environ.get("ADAPTER_LOG_LEVEL", "ERROR").upper()

# Janis Rubins step 2: Set up logging
logger = logging.getLogger(__name__)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(
    logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s]: %(message)s")
)
if not logger.handlers:
    logger.addHandler(handler)


class BaseAdapter(abc.ABC):
    """
    Janis Rubins step 3: Abstract base class for adapters.
    Methods:
    - match(data: dict) -> bool: Checks if this adapter can handle the given data format.
    - adapt(data: dict) -> dict: Transforms data into a standardized UI format.

    Making the code flexible:
    - Additional adapter-specific configs can be read from ENV or passed in constructor if needed.
    - Logging at each step helps trace adapter usage.
    """

    @abc.abstractmethod
    def match(self, data: dict) -> bool:
        pass

    @abc.abstractmethod
    def adapt(self, data: dict) -> dict:
        pass

    def __init__(self):
        # Janis Rubins step 4: If adapters need configuration from environment, do it here.
        # For now, no adapter-specific ENV usage. This is a placeholder for flexibility.
        pass

    def log_match_attempt(self, data: dict):
        # Janis Rubins step 5: Log attempts to match.
        logger.debug(
            f"Attempting to match {self.__class__.__name__} for data keys: {list(data.keys())}"
        )

    def log_adapt_start(self, data: dict):
        # Janis Rubins step 6: Log start of adaptation.
        logger.debug(f"{self.__class__.__name__} adapting data.")
