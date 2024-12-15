import os
import sys
import re
import logging
import time
from typing import Any, Dict, Optional, List
import threading

"""
This module provides security-related functions and rate limiting to protect against malicious inputs and denial-of-service attempts.
Key features:
- Flexible configuration via environment variables for maximum adaptability.
- Efficient checks (precompiled regex, minimal overhead) to ensure high performance.
- Suspicious pattern detection and identifier validation to prevent injection attacks.
- Optional rate limiting as a basic anti-DoS measure, easily integrable with external systems.
- Deep logging for full traceability without code changes, only environment tweaks.

All parameters (sizes, patterns, rate limits) are environment-driven, enabling quick response to emerging threats.
The design prioritizes security without compromising system performance.
"""

#######################
# Step 1: Environment Config
#######################
MAX_INPUT_SIZE = int(os.environ.get("MAX_INPUT_SIZE", "1048576"))  # Default 1MB, can adjust via env
SUSPICIOUS_PATTERNS_ENV = os.environ.get("SUSPICIOUS_PATTERNS",
    "__proto__,constructor,prototype,<script,eval(,settimeout,setinterval,function(,javascript:,data:,vbscript:,onerror=,onload=")
SUSPICIOUS_PATTERNS = [p.strip() for p in SUSPICIOUS_PATTERNS_ENV.split(",") if p.strip()]

IDENTIFIER_PATTERN = os.environ.get("IDENTIFIER_PATTERN", r'^[a-zA-Z0-9_\-]{1,64}$')

RATE_LIMIT_ENABLED = os.environ.get("RATE_LIMIT_ENABLED", "false").lower() == "true"
RATE_LIMIT_MAX_REQUESTS = int(os.environ.get("RATE_LIMIT_MAX_REQUESTS", 100))
RATE_LIMIT_WINDOW = int(os.environ.get("RATE_LIMIT_WINDOW", 60))

SECURITY_LOG_LEVEL = os.environ.get("SECURITY_LOG_LEVEL", "ERROR").upper()

#######################
# Step 2: Logging Setup
#######################
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(SECURITY_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)
handler.setFormatter(logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s'))
logger.addHandler(handler)

#######################
# Step 3: Precompile Patterns for Efficiency
#######################
# Compile identifier regex for fast validation
identifier_regex = re.compile(IDENTIFIER_PATTERN)

# Combine suspicious patterns into a single regex for efficient scanning
# Escape patterns to avoid regex injection
escaped_patterns = [re.escape(p) for p in SUSPICIOUS_PATTERNS if p]
if escaped_patterns:
    suspicious_regex = re.compile(r'(' + '|'.join(escaped_patterns) + ')', re.IGNORECASE)
else:
    # If no patterns provided, compile a no-op regex that never matches
    suspicious_regex = re.compile(r'(?!)')

#######################
# Step 4: Input Validation Functions
#######################
def check_input_size(data: Any) -> bool:
    """
    Check if input data's size (in UTF-8 bytes) is within MAX_INPUT_SIZE.
    Returns True if within limits, False otherwise.
    Minimizing overhead: just one encode operation.
    """
    data_str = str(data)
    size = len(data_str.encode('utf-8'))
    if size > MAX_INPUT_SIZE:
        logger.warning(f"Input size {size} bytes exceeds {MAX_INPUT_SIZE} bytes limit.")
        return False
    return True

def check_suspicious_patterns(data: Any) -> bool:
    """
    Scan input data for suspicious patterns indicating possible attacks.
    Returns True if no malicious pattern found, False if found.
    Using a single compiled regex for minimal overhead.
    """
    data_str = str(data)
    if suspicious_regex.search(data_str):
        logger.warning("Suspicious pattern detected in input.")
        return False
    return True

def is_safe_identifier(value: str) -> bool:
    """
    Validate identifier (e.g., function/widget name) against IDENTIFIER_PATTERN.
    If doesn't match, considered unsafe.
    """
    if identifier_regex.match(value):
        return True
    logger.warning(f"Identifier '{value}' does not match pattern: {IDENTIFIER_PATTERN}")
    return False

def validate_input(data: Any) -> bool:
    """
    Comprehensive input validation: size check + suspicious pattern check.
    Returns True if input is safe, False otherwise.
    Minimizing overhead by short-circuit evaluation.
    """
    return check_input_size(data) and check_suspicious_patterns(data)

#######################
# Step 5: Rate Limiter (Basic Anti-DoS)
#######################
class RateLimiter:
    """
    Simple in-memory rate limiter keyed by a client-specific identifier (e.g., IP).
    If RATE_LIMIT_ENABLED=True, it tracks requests and blocks if they exceed RATE_LIMIT_MAX_REQUESTS
    within RATE_LIMIT_WINDOW seconds.

    This design:
    - Thread-safe (lock-protected)
    - Minimal overhead for lookups
    - Flexible: Just change env vars to alter rate limit behavior
    For large-scale or distributed scenarios, consider external solutions (Redis-based or separate service).
    """
    def __init__(self, max_requests: int, window: int, enabled: bool):
        self.max_requests = max_requests
        self.window = window
        self.enabled = enabled
        self.requests: Dict[str, List[float]] = {}
        self.lock = threading.Lock()

    def check(self, key: str) -> bool:
        """
        Check if this request from 'key' is allowed.
        Returns True if allowed, False if exceeded rate limit.
        """
        if not self.enabled:
            return True

        now = time.time()
        cutoff = now - self.window
        with self.lock:
            if key not in self.requests:
                self.requests[key] = []
            # Purge old timestamps
            self.requests[key] = [t for t in self.requests[key] if t >= cutoff]

            if len(self.requests[key]) >= self.max_requests:
                logger.warning(f"Rate limit exceeded for {key}. Requests in last {self.window}s: {len(self.requests[key])}")
                return False

            self.requests[key].append(now)
            return True

    def clear(self):
        """
        Clears all recorded requests. Useful for an admin endpoint to reset rate limits instantly.
        """
        with self.lock:
            self.requests.clear()
            logger.info("Rate limit data cleared.")

#######################
# Step 6: Initialize global rate limiter instance
#######################
global_rate_limiter = RateLimiter(RATE_LIMIT_MAX_REQUESTS, RATE_LIMIT_WINDOW, RATE_LIMIT_ENABLED)

#######################
# Step 7: Integration helpers
#######################
def apply_rate_limit(key: str) -> bool:
    """
    Checks rate limit for a given key (like client IP).
    Return True if request allowed, False if blocked.
    """
    return global_rate_limiter.check(key)

def reset_rate_limiter():
    """
    Clears global rate limiter data, can be called by admin code or tests.
    """
    global_rate_limiter.clear()

#######################
# Step 8: Future Enhancements (No code changes needed)
#######################
# - Integrate distributed caching or rate limiting (e.g., Redis-based rate limiting)
# - Add a whitelist/blacklist mechanism via environment variables for known trusted/untrusted keys
# - Export metrics (e.g., count of blocked requests) to external monitoring tools
# - Dynamically reload SUSPICIOUS_PATTERNS, IDENTIFIER_PATTERN, or RATE_LIMIT settings on-the-fly if environment vars change

#######################
# Code is now flexible, secure, and efficient:
# - High performance: Precompiled regex, minimal data scans
# - Flexible: All settings from environment variables
# - Easy integration: Just import and call validate_input(), is_safe_identifier(), apply_rate_limit().
# - Logging at all critical steps for auditing and debugging.
#######################
