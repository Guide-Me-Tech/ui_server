import logging
import time
import json
import os
from fastapi import FastAPI, Request, Response
from configuration_manager.configuration_manager import (
    ConfigIDToPath,
    ConfigPath,
    ConfigsManager,
    UIBuilder,
)
from utils.users import get_users, get_api_keys
from functions_to_format.mapper import Formatter, functions_mapper

# Janis Rubins: Setting detailed logger, every detail at DEBUG for diagnostics, step-labeled
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)  # Janis Rubins: ensure debug level for deep insights
handler = logging.StreamHandler()
formatter = logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s]: %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# Janis Rubins: Pre-load users & api_keys once to minimize disk IO, saving system resources
users = get_users()  # Janis Rubins: STEP 1: Loaded users into memory
api_keys = get_api_keys()  # Janis Rubins: STEP 2: Loaded api_keys into memory


# Janis Rubins: Decorators for timing & steps
def timed(func):
    # Janis Rubins: measure sync function execution time & log steps
    def wrapper(*args, **kwargs):
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
            end = time.perf_counter()
            elapsed = end - start
            logger.debug(f"STEP FINAL: {func.__name__} done, elapsed={elapsed:.6f}s")
            logger.debug(f"--- END {func.__name__} ---\n")

    return wrapper


def timed_async(func):
    # Janis Rubins: measure async function execution & deep step logging
    async def wrapper(*args, **kwargs):
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


app = FastAPI()  # Janis Rubins: STEP 3: FastAPI initialized

# Janis Rubins: Initialize configs once, reusing memory and avoiding overhead
configs = ConfigsManager()  # Janis Rubins: STEP 4: ConfigsManager instance ready


def authorized(api_key) -> bool:
    # Janis Rubins: Simple lookup in api_keys dict - O(1) check, very fast
    # STEP 1: Check API key existence
    is_auth = api_key in api_keys
    logger.debug(f"STEP 2: authorized(api_key={api_key}) -> {is_auth}")
    return is_auth


formatter = Formatter()  # Janis Rubins: STEP 5: Formatter ready for UI formatting


@app.post("/config")
@timed_async
async def new_config(request: Request, name: str):
    # Janis Rubins: Adding a new config with logging steps
    logger.debug("STEP 1: POST /config called")
    api_key = request.headers.get("X-API-Key")
    logger.debug(f"STEP 2: Extracted api_key={api_key}")
    if not authorized(api_key=api_key):
        logger.debug("STEP 3: Not authorized to add config")
        return Response(status_code=401)

    username = api_keys[api_key]
    logger.debug(f"STEP 4: Authorized user='{username}', name='{name}' adding config")
    data = await request.json()  # Janis Rubins: direct json parse to save CPU & memory
    logger.debug(f"STEP 5: JSON data for new config: {data}")
    configs.add_config(username, data, name)  # Janis Rubins: directly add config
    logger.debug(f"STEP 6: Config '{name}' added idx={configs.idx}")
    return {
        "status": "success",
        "message": f"Configuration {name} added successfully",
        "id": configs.idx,
    }


@app.put("/config/{idx}")
@timed_async
async def update_config_by_id(request: Request, idx: str):
    # Janis Rubins: Update not implemented
    logger.debug(f"STEP 1: PUT /config/{idx} called - Not implemented")
    raise NotImplementedError("Update not implemented yet.")


@app.delete("/config/{idx}")
@timed
def delete_config_by_id(request: Request, idx: str):
    # Janis Rubins: Deleting config by id, ensure authorization & log steps
    logger.debug(f"STEP 1: DELETE /config/{idx}")
    api_key = request.headers.get("X-API-Key")
    logger.debug(f"STEP 2: api_key={api_key}")
    if not authorized(api_key=api_key):
        logger.debug("STEP 3: Not authorized to delete config")
        return Response(status_code=401)
    logger.debug(f"STEP 4: Authorized, deleting config id={idx}")
    configs.delete_config_by_id(int(idx))
    logger.debug(f"STEP 5: Config '{idx}' deleted")
    return {
        "status": "success",
        "message": f"Configuration {idx} deleted successfully",
    }


@app.get("/config")
@timed
def get_all_configs(request: Request):
    # Janis Rubins: Get all configs for authorized user
    logger.debug("STEP 1: GET /config called")
    api_key = request.headers.get("X-API-Key")
    logger.debug(f"STEP 2: api_key={api_key}")
    if not authorized(api_key=api_key):
        logger.debug("STEP 3: Not authorized to get all configs")
        return Response(status_code=401)
    username = api_keys[api_key]
    logger.debug(f"STEP 4: user='{username}' retrieving configs")
    configs_data = configs.get_configs(username)
    logger.debug(f"STEP 5: Configs retrieved: {configs_data}")
    return configs_data


@app.get("/config/{idx}")
@timed
def get_config(request: Request, idx: str):
    # Janis Rubins: Get single config by id
    logger.debug(f"STEP 1: GET /config/{idx}")
    config_data = configs.get_config_by_id(int(idx))
    logger.debug(f"STEP 2: config_data={config_data}")
    return config_data


@app.get("/build/ui/{idx}")
@timed_async
async def build_ui(request: Request, idx: str):
    # Janis Rubins: Build UI from config & given data
    logger.debug(f"STEP 1: GET /build/ui/{idx}")
    data = await request.json()
    logger.debug(f"STEP 2: UI build input data: {data}")
    config = configs.get_config_by_id(int(idx))
    logger.debug(f"STEP 3: config={config} retrieved for UI")
    result = UIBuilder.build_ui(config, data)  # Janis Rubins: minimal overhead call
    logger.debug(f"STEP 4: UI build result={result}")
    return result


@app.get("/chat/v2/build_ui/text")
@timed_async
async def format_data(request: Request):
    # Janis Rubins: Format text widget data
    logger.debug("STEP 1: GET /chat/v2/build_ui/text")
    data = await request.json()
    logger.debug(f"STEP 2: data={data} for text widget format")
    result = formatter.format_widget(widget_name="text_widget", data=data)
    logger.debug(f"STEP 3: Formatted text widget result={result}")
    return result


@app.get("/chat/v2/build_ui/actions")
async def format_data_v2(request: Request):
    # Janis Rubins: call function from functions_mapper for actions
    print("BUILD UI")
    logger.debug("STEP 1: GET /chat/v2/build_ui/actions")
    data = await request.json()
    logger.debug(f"STEP 2: data={data} for actions")
    func_name = data["function_name"]
    logger.debug(f"STEP 3: func_name={func_name}")
    func = functions_mapper.get(func_name)
    if func is None:
        logger.debug(f"STEP 4: No function found for {func_name}")
        return Response(status_code=400, content="Function not found.")
    print(data)
    if data["llm_output"] == "finish":
        return {"schema": "finish", "data": "finish"}
    data["backend_output"] = json.loads(data["backend_output"])
    logger.debug("STEP 5: Found function, invoking now")
    result = func(data["llm_output"], data["backend_output"])
    logger.debug(f"STEP 6: actions result={result}")
    return result
