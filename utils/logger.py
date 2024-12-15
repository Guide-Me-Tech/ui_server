import logging
import os
import sys
from typing import Optional

"""
Why this code is needed:
- Centralizes logging setup for the entire application.
- Allows flexible configuration of log levels, formats, and handlers via environment variables.
- Provides a foundation for deep logging that aids in diagnosing issues, tracking performance,
  and integrating with external monitoring systems.
- Ensures changes to logging behavior can be done without modifying code, just by adjusting environment variables.
- Maintains compatibility with old logic while adding flexibility, security, and efficiency.
"""

# Janis Rubins step 1: Load environment variables for flexible configuration
LOG_LEVEL = os.environ.get("LOG_LEVEL", "ERROR").upper()     # Default ERROR level if not set
LOG_FORMAT = os.environ.get("LOG_FORMAT", "[%(asctime)s][%(levelname)s][%(name)s]: %(message)s")
LOG_DATE_FORMAT = os.environ.get("LOG_DATE_FORMAT", "%Y-%m-%d %H:%M:%S")
LOG_OUTPUT = os.environ.get("LOG_OUTPUT", "stdout")          # 'stdout', 'stderr', or a file path
LOG_MODULE_LEVELS = os.environ.get("LOG_MODULE_LEVELS", "")
# Example LOG_MODULE_LEVELS: "moduleA=DEBUG;moduleB=INFO"

# Janis Rubins step 2: Parse LOG_MODULE_LEVELS for per-module settings
module_levels = {}
if LOG_MODULE_LEVELS:
    for entry in LOG_MODULE_LEVELS.split(";"):
        if "=" in entry:
            mod, lvl = entry.split("=", 1)
            mod = mod.strip()
            lvl = lvl.strip().upper()
            if mod and lvl:
                module_levels[mod] = lvl

# Janis Rubins step 3: Function to configure the root logger
def configure_root_logger():
    """
    Configures the root logger using environment variables.
    Adjusting LOG_LEVEL or LOG_OUTPUT changes behavior without modifying code.
    This allows easy adaptation to different environments (dev, test, prod).
    """
    level = logging.getLevelName(LOG_LEVEL)

    # Set root logger level
    logging.root.setLevel(level)

    # Remove existing handlers to avoid duplicates if reconfigured
    for h in logging.root.handlers[:]:
        logging.root.removeHandler(h)

    # Determine output handler type
    if LOG_OUTPUT.lower() in ["stdout", "stderr"]:
        stream = sys.stdout if LOG_OUTPUT.lower() == "stdout" else sys.stderr
        handler = logging.StreamHandler(stream)
    else:
        # If LOG_OUTPUT is a path, we write logs to that file
        handler = logging.FileHandler(LOG_OUTPUT)

    # Create formatter with date format for performance/time tracing
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    handler.setFormatter(formatter)
    logging.root.addHandler(handler)

# Janis Rubins step 4: Apply module-specific levels
def apply_module_levels():
    """
    Apply per-module log levels specified in LOG_MODULE_LEVELS.
    This provides granular control over logging without code changes.
    Example:
    export LOG_MODULE_LEVELS="my_module=DEBUG;another_module=INFO"
    """
    for mod, lvl in module_levels.items():
        numeric_level = logging.getLevelName(lvl)
        logging.getLogger(mod).setLevel(numeric_level)

# Janis Rubins step 5: Initialize logging configuration
configure_root_logger()
apply_module_levels()

# Janis Rubins step 6: Provide a helper function for creating named loggers
def get_logger(name: str, level: Optional[str] = None) -> logging.Logger:
    """
    Returns a logger with the given name.
    Optionally set a specific log level for that logger, overriding defaults.

    This allows creating specialized loggers for certain modules or components,
    making it easy to debug specific parts of the code without affecting others.

    :param name: Logger name (often __name__)
    :param level: Optional explicit level (e.g. "DEBUG", "INFO")
    :return: Configured logging.Logger instance
    """
    logger = logging.getLogger(name)
    if level is not None:
        numeric_level = logging.getLevelName(level.upper())
        logger.setLevel(numeric_level)
    else:
        # If module level was set via environment variable, it applies automatically
        pass
    return logger

# Janis Rubins step 7: Example usage (commented out)
# test_logger = get_logger(__name__)
# test_logger.debug("Logger initialized with current configuration.")

# Janis Rubins step 8: Conclusion
# This file sets up a flexible and deep logging system.
# - Configuration via ENV: easy to adapt to different setups
# - Per-module log levels: pinpoint issues in specific modules
# - Deep logging, timestamps, and integration with external tools is straightforward.
