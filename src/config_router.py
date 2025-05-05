from fastapi import APIRouter, Request, Response, FastAPI
from fastapi.responses import JSONResponse
from typing import Dict, Any, Optional, List, Set
import re
import datetime
import time
import json
import hashlib
import importlib.util
import psutil
from pathlib import Path
from datetime import timedelta
from conf import logger
from configuration_manager.configuration_manager import (
    ConfigsManager,
    UIBuilder,
)
from utils.users import get_users, get_api_keys
from functions_to_format.mapper import Formatter, functions_mapper


# Function to check memory usage
def check_memory_usage():
    memory_percent = psutil.virtual_memory().percent
    return memory_percent < 90  # Return True if memory usage is below 90%


# Janis Rubins step 8: Timing decorators for sync and async endpoints
def timed(func):
    def wrapper(*args, **kwargs):
        if not check_memory_usage():
            logger.error("Memory limit exceeded")
            return Response(status_code=503, content="Service unavailable")
        start = time.perf_counter()
        logger.debug(f"--- START {func.__name__} ---")
        logger.debug(f"STEP 1: Entering {func.__name__} args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"STEP 2: {func.__name__} result={result}")
            return result
        except Exception as e:
            logger.debug(
                f"STEP X: Exception in {func.__name__} error={e}", exc_info=True
            )
            return Response(status_code=500, content=str(e))
        finally:
            elapsed = time.perf_counter() - start
            logger.debug(f"STEP FINAL: {func.__name__} done, elapsed={elapsed:.6f}s")
            logger.debug(f"--- END {func.__name__} ---\n")

    return wrapper


def timed_async(func):
    async def wrapper(*args, **kwargs):
        if not check_memory_usage():
            logger.error("Memory limit exceeded")
            return Response(status_code=503, content="Service unavailable")

        start = time.perf_counter()
        logger.debug(f"--- START {func.__name__} (async) ---")
        logger.debug(
            f"STEP 1: Entering {func.__name__}(async) args={args}, kwargs={kwargs}"
        )
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"STEP 2: {func.__name__}(async) result={result}")
            return result
        except Exception as e:
            logger.debug(
                f"STEP X: Exception in {func.__name__}(async) error={e}", exc_info=True
            )
            return Response(status_code=500, content=str(e))
        finally:
            end = time.perf_counter()
            elapsed = end - start
            logger.debug(
                f"STEP FINAL: {func.__name__}(async) done, elapsed={elapsed:.6f}s"
            )
            logger.debug(f"--- END {func.__name__}(async) ---\n")

    return wrapper


# Get API keys
api_keys = get_api_keys()

# Janis Rubins: Initialize configs once, reusing memory and avoiding overhead
configs = ConfigsManager()  # Janis Rubins: STEP 4: ConfigsManager instance ready


def authorized(api_key) -> bool:
    is_auth = api_key in api_keys
    logger.debug(f"STEP 2: authorized(api_key={api_key}) -> {is_auth}")
    return is_auth


# Janis Rubins step 10: Initialize configs manager and formatter
configs = ConfigsManager()
formatter = Formatter()


# Janis Rubins step 11: Base data adapter and known/fallback adapters
class BaseDataAdapter:
    def match(self, data: dict) -> bool:
        return False

    def adapt(self, data: dict) -> dict:
        return data


class KnownFormatAdapter(BaseDataAdapter):
    def match(self, data: dict) -> bool:
        return "expected_key" in data

    def adapt(self, data: dict) -> dict:
        return {"type": "known_format", "content": data["expected_key"]}


class FallbackAdapter(BaseDataAdapter):
    def adapt(self, data: dict) -> dict:
        return {
            "type": "fallback",
            "message": "Data format not recognized. Minimal UI displayed.",
        }


class DataAdapterFactory:
    # Janis Rubins step 12: Adapts data using known or fallback adapters
    def __init__(self):
        self.adapters: List[BaseDataAdapter] = [KnownFormatAdapter()]
        self.fallback = FallbackAdapter()

    def adapt_data(self, data: dict) -> dict:
        logger.debug("STEP A: Starting data adaptation")
        for adapter in self.adapters:
            logger.debug(f"STEP B: Checking {adapter.__class__.__name__}")
            if adapter.match(data):
                logger.debug(f"STEP C: {adapter.__class__.__name__} matched")
                adapted = adapter.adapt(data)
                logger.debug(f"STEP D: adapted_data={adapted}")
                return adapted
        logger.warning("STEP E: No adapter matched, using fallback")
        adapted = self.fallback.adapt(data)
        logger.debug(f"STEP F: fallback_adapted_data={adapted}")
        return adapted


data_adapter_factory = DataAdapterFactory()


def is_safe_identifier(identifier):
    if not identifier:
        return False
    return bool(SecurityConstants.SAFE_PATTERN.match(str(identifier)))


def load_functions_from_plugins(plugin_dir: str = "plugins"):
    # Janis Rubins step 13: Dynamically load functions from plugins
    logger.debug("STEP G: Loading functions from plugins")
    p = Path(plugin_dir)
    if not p.exists():
        logger.debug("STEP H: No plugins directory, skipping")
        return
    for py_file in p.glob("*.py"):
        logger.debug(f"STEP I: Loading plugin {py_file}")
        # Check plugin size
        if py_file.stat().st_size > SecurityConstants.MAX_PAYLOAD_SIZE:
            logger.warning(f"Plugin {py_file} exceeds size limit, skipping.")
            continue

        # Calculate file hash for integrity logging (not blocking)
        file_hash = hashlib.sha256(py_file.read_bytes()).hexdigest()
        logger.debug(f"STEP I2: Plugin {py_file} hash={file_hash[:8]}...")

        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "register_functions"):
            plugin_funcs = mod.register_functions()
            # Validate function names
            safe_funcs = {
                name: func
                for name, func in plugin_funcs.items()
                if is_safe_identifier(name)
            }
            if len(safe_funcs) < len(plugin_funcs):
                logger.warning(
                    "Some plugin functions had unsafe names and were skipped."
                )
            logger.debug(f"STEP J: Loaded functions: {list(safe_funcs.keys())}")
            functions_mapper.update(safe_funcs)


load_functions_from_plugins()

# Initialize router
router = APIRouter(tags=["ui"])


# Janis Rubins step 14: Global exception handler for structured JSON errors
# @router.exception_handler(Exception)
# async def global_exception_handler(request: Request, exc: Exception):
#     logger.error(f"Global Exception: {exc}", exc_info=True)
#     return JSONResponse(
#         status_code=500, content={"error": "Internal server error", "details": str(exc)}
#     )


# Janis Rubins step 7: Rate Limiter for controlling request rates
class RateLimiter:
    def __init__(self):
        self.requests: Dict[str, List[datetime.datetime]] = {}
        self.blocked_ips: Set[str] = set()
        self.last_cleanup = datetime.datetime.now()

    async def cleanup(self):
        now = datetime.datetime.now()
        if (now - self.last_cleanup).seconds > SecurityConstants.RATE_LIMIT_WINDOW:
            for ip in list(self.requests.keys()):
                self.requests[ip] = [
                    t
                    for t in self.requests[ip]
                    if (now - t)
                    < timedelta(seconds=SecurityConstants.RATE_LIMIT_WINDOW)
                ]
                if not self.requests[ip]:
                    del self.requests[ip]
            self.last_cleanup = now

    async def check_rate_limit(self, ip: str) -> bool:
        if ip in self.blocked_ips:
            logger.warning(f"Blocked IP attempted request: {ip}")
            return False

        await self.cleanup()
        now = datetime.datetime.now()

        if ip not in self.requests:
            self.requests[ip] = []

        self.requests[ip].append(now)
        recent_requests = len(
            [
                t
                for t in self.requests[ip]
                if (now - t) < timedelta(seconds=SecurityConstants.RATE_LIMIT_WINDOW)
            ]
        )

        if recent_requests > SecurityConstants.MAX_REQUEST_RATE:
            self.blocked_ips.add(ip)
            logger.warning(f"IP {ip} blocked for excessive requests")
            return False

        return True


rate_limiter = RateLimiter()


# Janis Rubins: Setting detailed logger, every detail at DEBUG for diagnostics, step-labeled
# Janis Rubins step 1: Security and Performance Constants
class SecurityConstants:
    MAX_PAYLOAD_SIZE = 1024 * 1024  # 1MB limit
    MAX_MEMORY_USAGE = 1024 * 1024 * 1024  # 1GB max memory (example)
    MAX_REQUEST_RATE = 100  # max requests per window
    RATE_LIMIT_WINDOW = 60  # seconds
    CACHE_SIZE = 1000
    SAFE_PATTERN = re.compile(r"^[a-zA-Z0-9_\-]{1,64}$")
    SUSPICIOUS_PATTERNS = [
        "__proto__",
        "constructor",
        "prototype",
        "<script",
        "eval(",
        "settimeout",
        "setinterval",
        "function(",
        "javascript:",
        "data:",
        "vbscript:",
        "onerror=",
        "onload=",
    ]


def sanitize_input(data: Any) -> Optional[Any]:
    # Janis Rubins step 6: Sanitize input, check size and suspicious patterns
    try:
        data_str = json.dumps(data)
        if len(data_str.encode()) > SecurityConstants.MAX_PAYLOAD_SIZE:
            logger.error("Input data exceeds size limit")
            return None

        if any(
            pattern in data_str.lower()
            for pattern in SecurityConstants.SUSPICIOUS_PATTERNS
        ):
            logger.error("Suspicious pattern detected in input")
            return None

        return data
    except Exception as e:
        logger.error(f"Sanitization error: {e}")
        return None


@router.post("/config")
@timed_async
async def new_config(request: Request, name: str):
    # Janis Rubins step 16: Add a new config
    api_key = request.headers.get("X-API-Key")
    if not is_safe_identifier(api_key):
        logger.error("Invalid API key format")
        return Response(status_code=401)

    if not authorized(api_key=api_key):
        return Response(status_code=401)

    if not is_safe_identifier(name):
        logger.error("Invalid config name format")
        return Response(status_code=400)

    data = await request.json()
    sanitized_data = sanitize_input(data)
    if sanitized_data is None:
        return Response(status_code=400, content="Invalid data")

    configs.add_config(api_keys[api_key], sanitized_data, name)
    return {
        "status": "success",
        "message": f"Configuration {name} added successfully",
        "id": configs.idx,
    }


@router.put("/config/{idx}")
@timed_async
async def update_config_by_id(request: Request, idx: str):
    # Janis Rubins step 17: Update not implemented
    raise NotImplementedError("Update not implemented.")


@router.delete("/config/{idx}")
@timed
def delete_config_by_id(request: Request, idx: str):
    # Janis Rubins step 18: Delete config by ID with authorization
    api_key = request.headers.get("X-API-Key")
    if not authorized(api_key=api_key):
        return Response(status_code=401)
    configs.delete_config_by_id(int(idx))
    return {
        "status": "success",
        "message": f"Configuration {idx} deleted successfully",
    }


@router.get("/config")
@timed
def get_all_configs(request: Request):
    # Janis Rubins step 19: Get all configs for authorized user
    api_key = request.headers.get("X-API-Key")
    if not authorized(api_key=api_key):
        return Response(status_code=401)
    username = api_keys[api_key]
    configs_data = configs.get_configs(username)
    return configs_data


@router.get("/config/{idx}")
@timed
def get_config(request: Request, idx: str):
    # Janis Rubins step 20: Get single config by ID
    config_data = configs.get_config_by_id(int(idx))
    return config_data


@router.get("/build/ui/{idx}")
@timed_async
async def build_ui(request: Request, idx: str):
    # Janis Rubins step 21: Build UI from config & given data
    data = await request.json()
    sanitized_data = sanitize_input(data)
    if sanitized_data is None:
        return Response(status_code=400, content="Invalid data")
    config = configs.get_config_by_id(int(idx))
    adapted_data = data_adapter_factory.adapt_data(sanitized_data)
    result = UIBuilder.build_ui(config, adapted_data)
    return result
