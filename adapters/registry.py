import os
import sys
import logging
import importlib
import glob
from typing import List, Type
from .base_adapter import BaseAdapter
from .default_adapter import FallbackAdapter

"""
Why this code is needed:
- Manages loading and registering adapters.
- Allows dynamic addition/removal of adapters without code changes, just by placing files or setting env vars.
- Tries adapters in order and uses fallback if none match.
- Detailed logging for each step: loading, registering, matching.

Environment Variables:
- ADAPTERS_DIR: directory to load adapters from (optional)
- ADAPTERS_LIST: comma-separated class paths (e.g., "my_adapters.JsonAdapter,my_adapters.XmlAdapter")
- ADAPTER_LOG_LEVEL: controls verbosity for adapter registry actions.

All steps are logged, aiding debugging and auditing adapter discovery.
"""

# Janis Rubins step 1: Load logging level from env
ADAPTER_LOG_LEVEL = os.environ.get("ADAPTER_LOG_LEVEL", "ERROR").upper()

# Janis Rubins step 2: Set up logging for registry
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(ADAPTER_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
if not logger.handlers:
    logger.addHandler(handler)

# Janis Rubins step 3: Read adapter configuration environment variables
ADAPTERS_DIR = os.environ.get("ADAPTERS_DIR", "")
ADAPTERS_LIST = os.environ.get("ADAPTERS_LIST", "")

class AdapterRegistry:
    """
    Janis Rubins step 4: AdapterRegistry manages adapter instances.
    - initialize() loads from ADAPTERS_LIST and ADAPTERS_DIR
    - register_adapter() to add adapters
    - find_adapter(data) tries adapters and returns first match or fallback.

    Flexible: Just add new adapters to dir or list, no code changes needed.
    """

    def __init__(self):
        self.adapters: List[BaseAdapter] = []

    def register_adapter(self, adapter_cls: Type[BaseAdapter]):
        # Janis Rubins step 5: Instantiate and register adapter
        adapter_instance = adapter_cls()
        self.adapters.append(adapter_instance)
        logger.debug(f"Registered adapter: {adapter_cls.__name__}")

    def load_adapters_from_list(self):
        """
        Janis Rubins step 6: Load adapters from ADAPTERS_LIST.
        Each entry like 'my_adapters.JsonAdapter'.
        """
        if not ADAPTERS_LIST:
            logger.debug("No ADAPTERS_LIST provided, skipping loading from list.")
            return
        for path in ADAPTERS_LIST.split(","):
            path = path.strip()
            if not path:
                continue
            try:
                module_name, class_name = path.rsplit(".", 1)
                mod = importlib.import_module(module_name)
                cls = getattr(mod, class_name)
                if issubclass(cls, BaseAdapter):
                    self.register_adapter(cls)
                else:
                    logger.warning(f"{class_name} is not a subclass of BaseAdapter.")
            except Exception as e:
                logger.error(f"Error loading adapter {path}: {e}", exc_info=True)

    def load_adapters_from_dir(self):
        """
        Janis Rubins step 7: Load adapters from a directory.
        Scans for .py files and imports classes that subclass BaseAdapter.
        """
        if not ADAPTERS_DIR or not os.path.isdir(ADAPTERS_DIR):
            logger.debug("No valid ADAPTERS_DIR provided, skipping loading from directory.")
            return
        py_files = glob.glob(os.path.join(ADAPTERS_DIR, "*.py"))
        for file_path in py_files:
            if os.path.basename(file_path) == "__init__.py":
                continue
            try:
                spec = importlib.util.spec_from_file_location(os.path.splitext(os.path.basename(file_path))[0], file_path)
                mod = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(mod)  # type: ignore
                for attr_name in dir(mod):
                    attr = getattr(mod, attr_name)
                    if isinstance(attr, type) and issubclass(attr, BaseAdapter) and attr is not BaseAdapter:
                        self.register_adapter(attr)
            except Exception as e:
                logger.error(f"Error loading adapters from {file_path}: {e}", exc_info=True)

    def initialize(self):
        # Janis Rubins step 8: Initialize by loading from list and dir
        logger.debug("Initializing adapters from list and directory.")
        self.load_adapters_from_list()
        self.load_adapters_from_dir()

        # Ensure fallback adapter at the end
        if not any(isinstance(a, FallbackAdapter) for a in self.adapters):
            self.register_adapter(FallbackAdapter)

    def get_adapters(self) -> List[BaseAdapter]:
        # Janis Rubins step 9: Return ordered list of adapters
        return self.adapters

    def find_adapter(self, data: dict) -> BaseAdapter:
        """
        Janis Rubins step 10: Find adapter that matches data.
        Logs each attempt and returns first match or fallback.
        """
        logger.debug("Searching for suitable adapter...")
        for adapter in self.adapters:
            adapter.log_match_attempt(data)
            if adapter.match(data):
                logger.debug(f"Adapter {adapter.__class__.__name__} matched data.")
                return adapter
        # If none matched, fallback is last adapter
        fallback = self.adapters[-1]
        logger.debug("No adapter matched, using fallback adapter.")
        return fallback


# Example usage (commented out):
# registry = AdapterRegistry()
# registry.initialize()
# chosen_adapter = registry.find_adapter({"some": "data"})
# result = chosen_adapter.adapt({"some": "data"})
