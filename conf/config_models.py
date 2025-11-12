from ast import Tuple
from dataclasses import dataclass
from typing import Optional
import os

import dotenv


@dataclass
class LogfireConfig:
    token: str


@dataclass
class SentryConfig:
    dsn: str


@dataclass
class OTELConfig:
    service_name: str = "ui_server"
    resource_attributes: str = (
        "deployment.environment=production,service.namespace=ui-server"
    )
    bsp_schedule_delay: int = 5000
    bsp_max_queue_size: int = 2048
    bsp_max_export_batch_size: int = 512
    bsp_export_timeout: int = 30000
    traces_sampler: str = "parentbased_traceidratio"
    traces_sampler_arg: float = 1.0
    exporter_otlp_endpoint: str = "http://tempo:4318/v1/traces"
    exporter_otlp_headers: Optional[str] = None
    console_export: bool = False


@dataclass
class UsageCollectionMongoConfig:
    database_name: str = "usage"
    collection_name: str = "ui_server"
    mongo_uri: str = "mongodb://admin:admin@localhost:27017"


@dataclass
class AppConfig:
    logfire: LogfireConfig
    sentry: SentryConfig
    otel: OTELConfig
    environment: str = "development"
    mongo: Optional[UsageCollectionMongoConfig] = None


def New() -> AppConfig:
    dotenv.load_dotenv(".env")
    # with open(".env", "r") as f:
    #     print("ENV FILE: ", f.read())

    # for key, value in os.environ.items():
    #     print(f"{key}: {value}")

    logfire_config = LogfireConfig(token=os.getenv("LOGFIRE_TOKEN"))
    sentry_config = SentryConfig(dsn=os.getenv("SENTRY_DSN"))
    otel_config = OTELConfig(
        service_name=os.getenv("SERVICE_NAME", "ui_server"),
        resource_attributes=os.getenv(
            "RESOURCE_ATTRIBUTES",
            "deployment.environment=PRODUCTION,service.namespace=ui-server",
        ),
        bsp_schedule_delay=int(os.getenv("BSP_SCHEDULE_DELAY", 5000)),
        bsp_max_queue_size=int(os.getenv("BSP_MAX_QUEUE_SIZE", 2048)),
        bsp_max_export_batch_size=int(os.getenv("BSP_MAX_EXPORT_BATCH_SIZE", 512)),
        bsp_export_timeout=int(os.getenv("BSP_EXPORT_TIMEOUT", 30000)),
        traces_sampler=os.getenv("TRACES_SAMPLER", "parentbased_traceidratio"),
        traces_sampler_arg=float(os.getenv("TRACES_SAMPLER_ARG", 1.0)),
        exporter_otlp_endpoint=os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT", "http://tempo:4318/v1/traces"
        ),
        exporter_otlp_headers=os.getenv("EXPORTER_OTLP_HEADERS", None),
        console_export=bool(os.getenv("CONSOLE_EXPORT", False)),
    )
    return AppConfig(
        environment=os.getenv("ENVIRONMENT", "development"),
        logfire=logfire_config,
        sentry=sentry_config,
        otel=otel_config,
        mongo=UsageCollectionMongoConfig(
            database_name=os.getenv("MONGO_DATABASE_NAME", "usage"),
            collection_name=os.getenv("MONGO_COLLECTION_NAME", "ui_server"),
            mongo_uri=os.getenv("MONGO_URI", "mongodb://admin:admin@localhost:27017"),
        ),
    )


config = New()
