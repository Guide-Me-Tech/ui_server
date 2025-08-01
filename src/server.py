from conf import logger
import json
import os
from typing import Optional, Any, Dict, List, Callable, Set, Union
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from models.build import BuildOutput, ErrorResponse
from functions_to_format.functions import functions_mapper
import sentry_sdk
try:
    version = open("version.txt", "r").read()
except Exception as e:
    version = "0"
finally:
    if version == "":
        version = "0"
logger.info("Starting server", env=os.getenv("ENVIRONMENT"), version=version)
# from src.config_router import router

app = FastAPI()


# delete all json files in functions_to_format/functions/
for file in os.listdir("."):
    if file.endswith(".json"):
        os.remove(os.path.join(".", file))
        logger.info(f"Deleted file: {file}")

# Serve static files
app.mount("/ui_server/static", StaticFiles(directory="static"), name="static")

# https://www.youtbe.com/watch?v=NTP4XdTjRK0
if os.getenv("ENVIRONMENT") == "production":
    sentry_sdk.init(
        dsn=os.getenv("SENTRY_DSN"),
        # Set traces_sample_rate to 1.0 to capture 100%
        # of transactions for tracing.
        traces_sample_rate=1.0,
        _experiments={
            # Set continuous_profiling_auto_start to True
            # to automatically start the profiler on when
            # possible.
            "continuous_profiling_auto_start": True,
        },
    )


class InputV3(BaseModel):
    function_name: str
    llm_output: Optional[str] = None
    backend_output: Union[Dict, List, None] = None


class InputV2(BaseModel):
    function_name: str
    llm_output: Optional[str] = None
    backend_output: Union[Dict, List, None] = None


@app.get("/health")
async def health():
    return "Ok"


@app.get("/chat/v2/build_ui/text")
async def format_data(request: Request):
    raise NotImplementedError()
    return ""


@app.post(
    "/chat/v3/build_ui",
    responses={200: {"model": BuildOutput}, 500: {"model": ErrorResponse}},
)
async def format_data_v3(input_data: InputV3):
    version = "v3"
    logger.debug("BUILD UI V3")
    try:
        logger.debug("Step 1: Entering /chat/v3/build_ui")
        func_name = input_data.function_name
        llm_output = input_data.llm_output
        backend_output = input_data.backend_output
        logger.debug(
            f"Received function_name={func_name} llm_output={llm_output} backend_output={backend_output} "
        )
        if not func_name or func_name not in functions_mapper:
            logger.warning(f"Invalid or missing function_name: {func_name}")
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(
                    error=f"Invalid or missing function_name: {func_name}",
                    traceback="",
                ).model_dump(),
            )

        logger.debug(f"Step 2: Found function {func_name}, invoking now")
        result: BuildOutput = functions_mapper[func_name](
            llm_output=llm_output, backend_output=backend_output, version=version
        )
        logger.debug(f"Step 3: Function result={result}")
        return result
    except Exception as e:
        logger.exception(f"Exception in /chat/v3/build_ui: {str(e)}")
        return JSONResponse(
            status_code=500,
            content=ErrorResponse(
                error=str(e), traceback=str(e.__traceback__)
            ).model_dump(),
        )


@app.get("/chat")
@app.post(
    "/chat/v2/build_ui/actions",
    responses={200: {"model": BuildOutput}, 500: {"model": ErrorResponse}},
)
async def format_data_v2(input_data: InputV2):
    version = "v2"
    # Janis Rubins: call function from functions_mapper for actions
    logger.debug("BUILD UI V2")
    logger.debug("STEP 1: GET /chat/v2/build_ui/actions")
    func_name = input_data.function_name
    if not func_name:
        return JSONResponse(
            status_code=400,
            content=ErrorResponse(error="function_name is required", traceback=""),
        )
    # with open("logs.json", "w") as f:
    #    json.dump(data, f)
    # sanitized_backend_output = sanitize_input(data.get("backend_output", {}))
    # if sanitized_llm_output is None or sanitized_backend_output is None:
    #     return Response(status_code=400, content="Invalid data")

    func = functions_mapper.get(func_name)
    if func is None:
        logger.debug(f"STEP 4: No function found for {func_name}")
        raise ValueError(f"No function found for {func_name}")
        # return chatbot answer
        func = functions_mapper.get("chatbot_answer")
    logger.debug(f"input_data: {input_data}")
    if func_name == "chatbot_answer":
        logger.debug("STEP 5: Found function, invoking now")
        result = func(input_data.llm_output, "")
        logger.debug(f"STEP 6: actions result={result}")
        return result
    if input_data.llm_output == "finish":
        return {"schema": "finish", "data": "finish"}
    logger.debug("STEP 5: Found function, invoking now")
    result = func(input_data.llm_output, input_data.backend_output, version)
    logger.debug(f"STEP 6: actions result={result}")
    return result
