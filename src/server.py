from conf import logger
import os
import time
from typing import Optional, Any, Dict, List, Callable, Set, Union
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from functions_to_format.functions.general.const_values import LanguageOptions
from functions_to_format.functions.general.utils import (
    upload_usages_async,
)
from models.build import BuildOutput, ErrorResponse
from functions_to_format.functions import functions_mapper
import sentry_sdk
from models.context import Context, LoggerContext
from telemetry import (
    setup_telemetry,
    TelemetryMiddleware,
    MetricsCollector,
    get_tracer,
    get_prometheus_metrics,
)

try:
    import tomllib

    with open("pyproject.toml", "rb") as f:
        pyproject_data = tomllib.load(f)
    version = pyproject_data.get("project", {}).get("version", "0")
except Exception as e:
    version = "0"
finally:
    if version == "":
        version = "0"
logger.info("Starting server", env=os.getenv("ENVIRONMENT"), version=version)

app = FastAPI()

# Setup telemetry
setup_telemetry(app, service_name="ui_server", version=version)

# Initialize metrics collector
metrics_collector = MetricsCollector()
tracer = get_tracer()

# Add telemetry middleware with metrics collector
app.add_middleware(TelemetryMiddleware, metrics_collector=metrics_collector)


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
    chat_id: Optional[str | None] = None
    api_key: Optional[str | None] = None


class InputV2(BaseModel):
    function_name: str
    llm_output: Optional[str] = None
    backend_output: Union[Dict, List, None] = None


health_counter = 0


@app.get("/health")
async def health():
    # here I need function to upload logs/usage to somewhere - can be [s3, mongo]
    # every health check is in 30 seconds so for 30 minutes I need to upload usages every 60 health checks
    global health_counter
    if health_counter % 60 == 0:
        await upload_usages_async()
    health_counter += 1

    return "Ok"


@app.get("/metrics")
async def metrics():
    """
    Prometheus metrics endpoint
    Returns metrics in Prometheus text format for scraping
    """
    return Response(
        content=get_prometheus_metrics(),
        media_type="text/plain; version=0.0.4; charset=utf-8",
    )


@app.get("/chat/v2/build_ui/text")
async def format_data(request: Request):
    raise NotImplementedError()
    return ""


@app.post(
    "/chat/v3/build_ui",
    responses={200: {"model": BuildOutput}, 500: {"model": ErrorResponse}},
)
async def format_data_v3(request: Request, input_data: InputV3):
    global logger
    version = "v3"

    start_time = time.time()
    logger = logger.bind(chat_id=input_data.chat_id)
    logger.info("BUILD UI V3")

    with tracer.start_as_current_span("build_ui_v3") as span:
        try:
            logger.info("Step 1: Entering /chat/v3/build_ui")
            language = LanguageOptions(request.headers.get("language", "ru"))
            func_name = input_data.function_name
            llm_output = input_data.llm_output or ""
            backend_output = (
                input_data.backend_output if input_data.backend_output else {}
            )
            api_key = input_data.api_key or ""

            # Add telemetry attributes
            span.set_attribute("function.name", func_name)
            span.set_attribute("function.version", version)
            span.set_attribute("language", language.value)

            logger.info(
                "Received request parameters",
                function_name=func_name,
                llm_output=llm_output,
                backend_output=backend_output,
                api_key=input_data.api_key,
            )

            if not func_name or func_name not in functions_mapper:
                logger.warning(f"Invalid or missing function_name: {func_name}")
                span.set_attribute("error", "invalid_function_name")
                return JSONResponse(
                    status_code=400,
                    content=ErrorResponse(
                        error=f"Invalid or missing function_name: {func_name}",
                        traceback="",
                    ).model_dump(),
                )

            logger.info(f"Step 2: Found function {func_name}, invoking now")

            # Time function execution
            func_start = time.time()
            context = Context(
                logger_context=LoggerContext(
                    chat_id=input_data.chat_id or "", logger=logger
                ),
                llm_output=llm_output,
                backend_output=backend_output,  # pyright: ignore[reportArgumentType]
                version=version,
                language=language,
                api_key=api_key,
            )

            result: BuildOutput = functions_mapper[func_name](
                context=context,
            )
            func_duration = (time.time() - func_start) * 1000

            # Record function metrics
            metrics_collector.record_function_invocation(
                function_name=func_name,
                duration_ms=func_duration,
                success=True,
                version=version,
            )

            span.set_attribute("function.duration_ms", func_duration)
            logger.info(f"Step 3: Function result={result}")

            return result
        except Exception as e:
            duration = (time.time() - start_time) * 1000

            # Record error metrics
            if "func_name" in locals():
                metrics_collector.record_function_invocation(
                    function_name=func_name,
                    duration_ms=duration,
                    success=False,
                    version=version,
                )

            span.record_exception(e)
            span.set_attribute("error.message", str(e))

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
    start_time = time.time()

    with tracer.start_as_current_span("build_ui_v2") as span:
        # Janis Rubins: call function from functions_mapper for actions
        logger.debug("BUILD UI V2")
        logger.debug("STEP 1: GET /chat/v2/build_ui/actions")
        func_name = input_data.function_name

        span.set_attribute("function.name", func_name)
        span.set_attribute("function.version", version)

        if not func_name:
            return JSONResponse(
                status_code=400,
                content=ErrorResponse(error="function_name is required", traceback=""),
            )

        func = functions_mapper.get(func_name)
        if func is None:
            logger.debug(f"STEP 4: No function found for {func_name}")
            span.set_attribute("error", "function_not_found")
            raise ValueError(f"No function found for {func_name}")
            # return chatbot answer
            func = functions_mapper.get("chatbot_answer")

        logger.debug(f"input_data: {input_data}")

        func_start = time.time()

        if func_name == "chatbot_answer":
            logger.debug("STEP 5: Found function, invoking now")
            result = func(input_data.llm_output, "")
            logger.debug(f"STEP 6: actions result={result}")

            func_duration = (time.time() - func_start) * 1000
            metrics_collector.record_function_invocation(
                function_name=func_name,
                duration_ms=func_duration,
                success=True,
                version=version,
            )

            return result

        if input_data.llm_output == "finish":
            return {"schema": "finish", "data": "finish"}

        logger.debug("STEP 5: Found function, invoking now")
        result = func(input_data.llm_output, input_data.backend_output, version)
        logger.debug(f"STEP 6: actions result={result}")

        func_duration = (time.time() - func_start) * 1000
        metrics_collector.record_function_invocation(
            function_name=func_name,
            duration_ms=func_duration,
            success=True,
            version=version,
        )

        return result
