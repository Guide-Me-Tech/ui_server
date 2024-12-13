import logging
import time
import json
import os
from typing import Optional, Any, Dict, List, Callable
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from pathlib import Path
import importlib.util

# Janis Rubins: High-Level Understanding
# This code dynamically handles unknown data formats from API responses, 
# builds UIs using adapters, and loads action functions from plugins. 
# It also provides structured JSON errors and thorough step-by-step logging for easy debugging.

# Janis Rubins: Key Concepts
# - DataAdapterFactory checks multiple adapters (like KnownFormatAdapter) to standardize unknown data.
# - If no adapter matches, a fallback adapter returns a minimal UI, ensuring the service never breaks.
# - Functions for actions are dynamically loaded from a plugins directory, allowing easy extension.
# - Every function and endpoint logs its steps with timing, making debugging straightforward.
# - A global exception handler returns JSON-formatted errors, simplifying error handling for consumers.

class UIBuilder:
    # Janis Rubins: Builds UI from config and adapted data.
    # Even if data is unknown, adapters ensure UIBuilder always receives something workable.
    @staticmethod
    def build_ui(config: dict, data: dict) -> dict:
        return {"ui": "built", "config_id": config.get("id"), "data": data}


class ConfigsManager:
    # Janis Rubins: In-memory config store.
    # Allows adding, deleting, and fetching configs per user without heavy resources.
    def __init__(self):
        self.configs = {}
        self.idx = 0

    def add_config(self, username: str, data: dict, name: str):
        self.idx += 1
        self.configs[self.idx] = {"id": self.idx, "user": username, "name": name, "data": data}

    def delete_config_by_id(self, idx: int):
        if idx in self.configs:
            del self.configs[idx]

    def get_configs(self, username: str):
        return [c for c in self.configs.values() if c["user"] == username]

    def get_config_by_id(self, idx: int):
        return self.configs.get(idx, {})


def get_users():
    # Janis Rubins: Stub for users. In a real scenario, fetch from DB.
    return {"user1": "User One"}

def get_api_keys():
    # Janis Rubins: Stub for API keys. Quickly verifies user identity.
    return {"test-api-key": "user1"}

class Formatter:
    # Janis Rubins: Formats UI widgets.
    # Simple logic now, but can be extended if widgets become complex.
    def format_widget(self, widget_name: str, data: dict) -> dict:
        return {"widget_name": widget_name, "formatted_data": data}


logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter_logging = logging.Formatter('[%(asctime)s][%(levelname)s][%(name)s]: %(message)s')
handler.setFormatter(formatter_logging)
logger.addHandler(handler)

users = get_users()
api_keys = get_api_keys()

def timed(func):
    # Janis Rubins: Decorator for sync endpoints.
    # Logs start, arguments, results, exceptions, and execution time, making performance visible.
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.debug(f"--- START {func.__name__} ---")
        logger.debug(f"STEP 1: Entering {func.__name__} args={args}, kwargs={kwargs}")
        try:
            result = func(*args, **kwargs)
            logger.debug(f"STEP 2: {func.__name__} result={result}")
            return result
        except Exception as e:
            logger.debug(f"STEP X: Exception in {func.__name__} error={e}", exc_info=True)
            return Response(status_code=500, content=str(e))
        finally:
            end = time.perf_counter()
            elapsed = end - start
            logger.debug(f"STEP FINAL: {func.__name__} done, elapsed={elapsed:.6f}s")
            logger.debug(f"--- END {func.__name__} ---\n")
    return wrapper

def timed_async(func):
    # Janis Rubins: Decorator for async endpoints.
    # Similar to timed, but for async functions, ensuring same thorough logging in async context.
    async def wrapper(*args, **kwargs):
        start = time.perf_counter()
        logger.debug(f"--- START {func.__name__} (async) ---")
        logger.debug(f"STEP 1: Entering {func.__name__}(async) args={args}, kwargs={kwargs}")
        try:
            result = await func(*args, **kwargs)
            logger.debug(f"STEP 2: {func.__name__}(async) result={result}")
            return result
        except Exception as e:
            logger.debug(f"STEP X: Exception in {func.__name__}(async) error={e}", exc_info=True)
            return Response(status_code=500, content=str(e))
        finally:
            end = time.perf_counter()
            elapsed = end - start
            logger.debug(f"STEP FINAL: {func.__name__}(async) done, elapsed={elapsed:.6f}s")
            logger.debug(f"--- END {func.__name__}(async) ---\n")
    return wrapper

app = FastAPI()

@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    # Janis Rubins: Global error handler.
    # Converts any uncaught exceptions into structured JSON for consistency and easier debugging.
    logger.error(f"Global Exception: {exc}", exc_info=True)
    return JSONResponse(status_code=500, content={"error": "Internal server error", "details": str(exc)})

configs = ConfigsManager()

def authorized(api_key) -> bool:
    # Janis Rubins: Simple authorization check.
    # Ensures only known API keys can modify configs or access data.
    is_auth = api_key in api_keys
    logger.debug(f"STEP 2: authorized(api_key={api_key}) -> {is_auth}")
    return is_auth

formatter = Formatter()

class BaseDataAdapter:
    # Janis Rubins: Base adapter class.
    # Adapters attempt to recognize and adapt unknown data formats for UI building.
    def match(self, data: dict) -> bool:
        return False
    def adapt(self, data: dict) -> dict:
        return data

class KnownFormatAdapter(BaseDataAdapter):
    # Janis Rubins: Example adapter for a known data format.
    # If 'expected_key' is found, adapt it into a known structure.
    def match(self, data: dict) -> bool:
        return "expected_key" in data
    def adapt(self, data: dict) -> dict:
        return {"type": "known_format", "content": data["expected_key"]}

class FallbackAdapter(BaseDataAdapter):
    # Janis Rubins: Fallback adapter.
    # If no known format matches, return a minimal UI, ensuring system never breaks.
    def adapt(self, data: dict) -> dict:
        return {
            "type": "fallback",
            "message": "Data format not recognized. Minimal UI displayed."
        }

class DataAdapterFactory:
    # Janis Rubins: Checks all adapters, picks one that matches the data, or fallback.
    # This makes the system resilient to unexpected Smartbank API responses.
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

functions_mapper = {}

def load_functions_from_plugins(plugin_dir: str = "plugins"):
    # Janis Rubins: Dynamically loads functions for actions from external plugin files.
    # Add a new plugin file, define 'register_functions()', and the code picks it up automatically.
    logger.debug("STEP G: Loading functions from plugins")
    p = Path(plugin_dir)
    if not p.exists():
        logger.debug("STEP H: No plugins directory, skipping")
        return
    for py_file in p.glob("*.py"):
        logger.debug(f"STEP I: Loading plugin {py_file}")
        spec = importlib.util.spec_from_file_location(py_file.stem, py_file)
        mod = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(mod)
        if hasattr(mod, "register_functions"):
            plugin_funcs = mod.register_functions()
            logger.debug(f"STEP J: Loaded functions: {list(plugin_funcs.keys())}")
            functions_mapper.update(plugin_funcs)

load_functions_from_plugins()

# Janis Rubins: Endpoints below interact with configs, build UI, and format data/widgets.
# They use decorators for timing/logging and rely on adapters & plugins for flexibility.

@app.post("/config")
@timed_async
async def new_config(request: Request, name: str):
    logger.debug("STEP 1: POST /config")
    api_key = request.headers.get("X-API-Key")
    logger.debug(f"STEP 2: api_key={api_key}")
    if not authorized(api_key=api_key):
        logger.debug("STEP 3: Not authorized")
        return Response(status_code=401)
    username = api_keys[api_key]
    logger.debug(f"STEP 4: Authorized user='{username}', adding config='{name}'")
    data = await request.json()
    logger.debug(f"STEP 5: received_data={data}")
    configs.add_config(username, data, name)
    logger.debug(f"STEP 6: config_id={configs.idx} added")
    return {
        "status": "success",
        "message": f"Configuration {name} added",
        "id": configs.idx,
    }

@app.put("/config/{idx}")
@timed_async
async def update_config_by_id(request: Request, idx: str):
    logger.debug(f"STEP 1: PUT /config/{idx}, not implemented")
    return Response(status_code=501, content="Update not implemented")

@app.delete("/config/{idx}")
@timed
def delete_config_by_id(request: Request, idx: str):
    logger.debug(f"STEP 1: DELETE /config/{idx}")
    api_key = request.headers.get("X-API-Key")
    logger.debug(f"STEP 2: api_key={api_key}")
    if not authorized(api_key=api_key):
        logger.debug("STEP 3: Not authorized")
        return Response(status_code=401)
    logger.debug(f"STEP 4: Deleting config_id={idx}")
    configs.delete_config_by_id(int(idx))
    logger.debug("STEP 5: Config deleted")
    return {
        "status": "success",
        "message": f"Configuration {idx} deleted",
    }

@app.get("/config")
@timed
def get_all_configs(request: Request):
    logger.debug("STEP 1: GET /config")
    api_key = request.headers.get("X-API-Key")
    logger.debug(f"STEP 2: api_key={api_key}")
    if not authorized(api_key=api_key):
        logger.debug("STEP 3: Not authorized")
        return Response(status_code=401)
    username = api_keys[api_key]
    logger.debug(f"STEP 4: fetching configs for {username}")
    configs_data = configs.get_configs(username)
    logger.debug(f"STEP 5: configs={configs_data}")
    return configs_data

@app.get("/config/{idx}")
@timed
def get_config(request: Request, idx: str):
    logger.debug(f"STEP 1: GET /config/{idx}")
    config_data = configs.get_config_by_id(int(idx))
    logger.debug(f"STEP 2: config_data={config_data}")
    return config_data

@app.get("/build/ui/{idx}")
@timed_async
async def build_ui(request: Request, idx: str):
    logger.debug(f"STEP 1: GET /build/ui/{idx}")
    data = await request.json()
    logger.debug(f"STEP 2: ui_input_data={data}")
    config = configs.get_config_by_id(int(idx))
    logger.debug(f"STEP 3: config={config}")
    adapted_data = data_adapter_factory.adapt_data(data)
    logger.debug(f"STEP 4: ui_adapted_data={adapted_data}")
    result = UIBuilder.build_ui(config, adapted_data)
    logger.debug(f"STEP 5: ui_result={result}")
    return result

@app.get("/chat/v2/build_ui/text")
@timed_async
async def format_data(request: Request):
    logger.debug("STEP 1: GET /chat/v2/build_ui/text")
    data = await request.json()
    logger.debug(f"STEP 2: text_data={data}")
    result = formatter.format_widget("text_widget", data)
    logger.debug(f"STEP 3: text_result={result}")
    return result

@app.get("/chat/v2/build_ui/actions")
@timed_async
async def format_data_v2(request: Request):
    logger.debug("STEP 1: GET /chat/v2/build_ui/actions")
    data = await request.json()
    logger.debug(f"STEP 2: actions_data={data}")
    func_name = data.get("function_name")

    if not func_name:
        logger.debug("STEP 3: function_name missing")
        return Response(status_code=400, content="function_name is required")

    logger.debug(f"STEP 4: looking_for_func={func_name}")
    func = functions_mapper.get(func_name)
    if func is None:
        logger.debug("STEP 5: func not found")
        return Response(status_code=400, content=f"Function '{func_name}' not found.")

    logger.debug("STEP 6: invoking_func")
    llm_output = data.get("llm_output", {})
    backend_output = data.get("backend_output", {})
    result = func(llm_output, backend_output)
    logger.debug(f"STEP 7: actions_result={result}")
    return result
