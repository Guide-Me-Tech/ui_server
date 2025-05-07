import logging
import time
import os
import re
from conf import logger
from functions_to_format.components import widgets
from functions_to_format.functions import functions_mapper, sdui_functions_map

# Janis Rubins changes:
# - Added deep logging at each step to understand exactly what's happening.
# - Used a high-performance approach: cached lookups, removed dead code, and minimized redundant operations.
# - Logging includes timing each method for performance insights.

# Janis Rubins step 1: Define constants for performance and security
# MAX_PAYLOAD_SIZE limits data size to prevent memory overhead
# SAFE_PATTERN ensures only safe identifiers are allowed
# SUSPICIOUS_PATTERNS checks for malicious patterns.
MAX_PAYLOAD_SIZE = 1024 * 1024
SAFE_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")
SUSPICIOUS_PATTERNS = ["__proto__", "constructor", "prototype", "<script"]


def is_safe_identifier(value: str) -> bool:
    return bool(SAFE_PATTERN.match(value))


# Janis Rubins step 5: Sanitize input to remove suspicious patterns and limit size
# Prevents loading or processing large or malicious payloads.
def sanitize_input(data):
    data_str = str(data)
    if len(data_str.encode()) > MAX_PAYLOAD_SIZE:
        logger.error("Input data exceeds size limit")
        return None
    if any(pattern in data_str.lower() for pattern in SUSPICIOUS_PATTERNS):
        logger.error("Suspicious pattern detected in input")
        return None
    return data


# Janis Rubins step 6: Decorator to measure execution time and log steps for performance insights
# Helps identify bottlenecks and optimize resource usage.
def timed(func):
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.debug(f"--- START {func.__name__} ---")
        logger.debug(f"Arguments: args={args}, kwargs={kwargs}")
        result = func(*args, **kwargs)
        end = time.perf_counter()
        logger.debug(f"{func.__name__} completed. Elapsed time: {end - start:.6f}s")
        logger.debug(f"--- END {func.__name__} ---\n")
        return result

    return wrapper
