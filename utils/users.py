import json
import os
import logging
import re
import psutil
import sys
from functools import lru_cache
from typing import Dict, Any


# Janis Rubins step 1: Define constants and patterns for flexibility and security
USER_FILE_PATH = os.environ.get("USER_FILE_PATH", "configs/users.json")
API_KEYS_FILE_PATH = os.environ.get("API_KEYS_FILE_PATH", "configs/api_keys.json")
MAX_FILE_SIZE = int(os.environ.get("MAX_USER_FILE_SIZE", 1024 * 1024))  # 1MB default
SUSPICIOUS_PATTERNS = [
    '__proto__', 'constructor', 'prototype', '<script', 'eval(', 'settimeout',
    'setinterval', 'function(', 'javascript:', 'data:', 'vbscript:', 'onerror=', 'onload='
]

# Janis Rubins step 2: Set up logging with optional debug mode
log_level = os.environ.get("LOG_LEVEL", "ERROR").upper()
level = logging.DEBUG if log_level == "DEBUG" else logging.ERROR
logger = logging.getLogger(__name__)
logger.setLevel(level)
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
logger.addHandler(handler)

def check_memory_usage() -> bool:
    # Janis Rubins step 3: Check memory usage to prevent overload
    try:
        process = psutil.Process(os.getpid())
        mem_usage = process.memory_info().rss
        # Example: if we had a max memory constraint, we could check it here
        # For now, just log memory usage for insights
        logger.debug(f"Memory usage: {mem_usage} bytes")
        return True
    except Exception as e:
        logger.error(f"Memory check error: {e}")
        return True

def file_is_safe(path: str) -> bool:
    # Janis Rubins step 4: Check if file exists, size within limits, and not suspicious
    if not os.path.exists(path):
        logger.error(f"File not found: {path}")
        return False
    size = os.path.getsize(path)
    if size > MAX_FILE_SIZE:
        logger.error(f"File {path} exceeds size limit ({size} bytes)")
        return False
    # Check for suspicious content patterns without loading full file if possible
    # Here we trust JSON file to be normal text, just read a chunk
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content_sample = f.read(min(size, 4096))  # read a small sample
        for pattern in SUSPICIOUS_PATTERNS:
            if pattern in content_sample.lower():
                logger.error(f"Suspicious pattern '{pattern}' detected in file {path}")
                return False
    return True

@lru_cache(maxsize=1)
def load_json(path: str) -> Dict[str, Any]:
    # Janis Rubins step 5: Load JSON file with caching, logging, and security checks
    logger.debug(f"Attempting to load JSON from {path}")
    if not check_memory_usage():
        logger.error("Memory limit exceeded before loading file")
        return {}

    if not file_is_safe(path):
        logger.error(f"File {path} not safe to load, returning empty dict.")
        return {}

    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
            logger.debug(f"Loaded JSON from {path}: keys={list(data.keys())}")
            return data
    except Exception as e:
        logger.error(f"Error loading JSON from {path}: {e}", exc_info=True)
        return {}

def get_users() -> Dict[str, Any]:
    # Janis Rubins step 6: get_users uses load_json for caching and logging
    logger.debug("get_users called")
    data = load_json(USER_FILE_PATH)
    if not isinstance(data, dict):
        logger.error("Users data is not a dictionary, returning empty dict.")
        return {}
    # Optional: Validate structure of user data if needed
    logger.debug("Users loaded successfully.")
    return data

def get_api_keys() -> Dict[str, Any]:
    # Janis Rubins step 7: get_api_keys similar to get_users, uses load_json
    logger.debug("get_api_keys called")
    data = load_json(API_KEYS_FILE_PATH)
    if not isinstance(data, dict):
        logger.error("API keys data is not a dictionary, returning empty dict.")
        return {}
    # Optional: Validate structure of API keys data if needed
    logger.debug("API keys loaded successfully.")
    return data

# Janis Rubins step 8:
# This file:
# - Uses environment variables for paths and size limits for flexibility.
# - Uses caching (lru_cache) to avoid re-loading the same file multiple times, saving CPU and I/O.
# - Performs size and suspicious pattern checks before loading, improving security.
# - Logs deeply at each step, aiding debugging and performance monitoring.
# - Maintains original logic (returning dicts of users/api_keys) but enhances safety, performance, and flexibility.
