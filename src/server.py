from fastapi import FastAPI, Request, Response, Depends
from configuration_manager.configuration_manager import (
    ConfigIDToPath,
    ConfigPath,
    ConfigsManager,
    UIBuilder,
)
from utils.users import get_users, get_api_keys
import os
import json

app = FastAPI()
users = get_users()
api_keys = get_api_keys()


def authorized(api_key) -> bool:
    if api_key in api_keys.keys():
        return True
    return False


configs = ConfigsManager()


@app.post("/config")
async def new_config(request: Request, name: str):
    # return Response(status_code=200)
    api_key = request.headers.get("X-API-Key")
    if not authorized(api_key=api_key):
        return Response(status_code=401)
    username = api_keys[api_key]
    data = await request.body()
    try:
        configs.add_config(username, json.loads(data), name)
    except Exception as e:
        return Response(status_code=500, content=e)
    return {
        "status": "success",
        "message": f"Configuration {name} added successfully",
        "id": configs.idx,
    }


@app.put("/config/{idx}")
async def update_config_by_id(request: Request, idx: str):
    raise NotImplementedError


@app.delete("/config/{idx}")
def delete_config_by_id(request: Request, idx: str):
    api_key = request.headers.get("X-API-Key")
    if not authorized(api_key=api_key):
        return Response(status_code=401)
    try:
        configs.delete_config_by_id(idx)
    except Exception as e:
        return Response(status_code=500, content=e)
    return {
        "status": "success",
        "message": f"Configuration {idx} deleted successfully",
    }


@app.get("/config")
def get_all_configs(request: Request):
    api_key = request.headers.get("X-API-Key")
    if not authorized(api_key=api_key):
        return Response(status_code=401)
    username = api_keys[api_key]
    try:
        return configs.get_configs(username)
    except Exception as e:
        return Response(status_code=500, content=e)


@app.get("/config/{idx}")
def get_config(request: Request, idx: str):
    configs.get_config_by_id(idx)


@app.get("/build/ui/{idx}")
async def build_ui(request: Request, idx: str):
    data = await request.json()
    print(data)
    try:
        config = configs.get_config_by_id(idx)
        print(config)
    except Exception as e:
        return Response(status_code=500, content=e)

    # apply configuration to UI
    return UIBuilder.build_ui(config, data)


from functions_to_format.mapper import Formatter
from functions_to_format.mapper import functions_mapper

formatter = Formatter()


@app.get("/chat/v2/build_ui/text")
async def format_data(request: Request):
    data = await request.json()
    return formatter.format_widget(widget_name="text_widget", data=data)
    # return
    # return Formatter().format_widget(data["widget_name"], data["data"])


@app.get("/chat/v2/build_ui/actions")
async def format_data_v2(request: Request):
    data = await request.json()
    return functions_mapper[data["function_name"]](
        data["llm_output"], data["backend_output"]
    )
