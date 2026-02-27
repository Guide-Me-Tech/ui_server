from ast import Tuple
from dataclasses import dataclass
from typing import Optional
import os

import dotenv
import yaml


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
    exporter_otlp_endpoint: str = "http://localhost:4318/v1/traces"
    exporter_otlp_headers: Optional[str] = None
    console_export: bool = False


@dataclass
class UsageCollectionMongoConfig:
    database_name: str = "usage"
    collection_name: str = "ui_server"
    mongo_uri: str = "mongodb://admin:admin@localhost:27017"


@dataclass
class SmartyConfig:
    base_url: str = "https://smarty.smartbank.uz"


@dataclass
class AppConfig:
    logfire: LogfireConfig
    sentry: SentryConfig
    otel: OTELConfig
    smarty: SmartyConfig
    environment: str = "development"
    mongo: UsageCollectionMongoConfig | None = None


def New() -> AppConfig:
    dotenv.load_dotenv(".env")

    environment = os.getenv("ENVIRONMENT", "development").lower()

    # Load per-environment defaults from config.yaml
    env_cfg: dict = {}
    try:
        with open("config.yaml", "r") as f:
            all_configs = yaml.safe_load(f) or {}
            env_cfg = all_configs.get(environment, {})
    except FileNotFoundError:
        pass

    logfire_cfg = env_cfg.get("logfire", {})
    sentry_cfg = env_cfg.get("sentry", {})
    otel_cfg = env_cfg.get("otel", {})
    mongo_cfg = env_cfg.get("mongo", {})
    smarty_cfg = env_cfg.get("smarty", {})
    # Resolve console_export: env var overrides yaml, yaml overrides False default
    console_export_env = os.getenv("CONSOLE_EXPORT")
    if console_export_env is not None:
        console_export = console_export_env.lower() in ("true", "1", "yes")
    else:
        console_export = bool(otel_cfg.get("console_export", False))

    logfire_config = LogfireConfig(
        token=os.getenv("LOGFIRE_TOKEN", logfire_cfg.get("token", ""))
    )
    sentry_config = SentryConfig(dsn=os.getenv("SENTRY_DSN", sentry_cfg.get("dsn", "")))
    otel_config = OTELConfig(
        service_name=os.getenv(
            "SERVICE_NAME", otel_cfg.get("service_name", "ui_server")
        ),
        resource_attributes=os.getenv(
            "RESOURCE_ATTRIBUTES",
            otel_cfg.get(
                "resource_attributes",
                "deployment.environment=production,service.namespace=ui-server",
            ),
        ),
        bsp_schedule_delay=int(
            os.getenv("BSP_SCHEDULE_DELAY", otel_cfg.get("bsp_schedule_delay", 5000))
        ),
        bsp_max_queue_size=int(
            os.getenv("BSP_MAX_QUEUE_SIZE", otel_cfg.get("bsp_max_queue_size", 2048))
        ),
        bsp_max_export_batch_size=int(
            os.getenv(
                "BSP_MAX_EXPORT_BATCH_SIZE",
                otel_cfg.get("bsp_max_export_batch_size", 512),
            )
        ),
        bsp_export_timeout=int(
            os.getenv("BSP_EXPORT_TIMEOUT", otel_cfg.get("bsp_export_timeout", 30000))
        ),
        traces_sampler=os.getenv(
            "TRACES_SAMPLER", otel_cfg.get("traces_sampler", "parentbased_traceidratio")
        ),
        traces_sampler_arg=float(
            os.getenv("TRACES_SAMPLER_ARG", otel_cfg.get("traces_sampler_arg", 1.0))
        ),
        exporter_otlp_endpoint=os.getenv(
            "OTEL_EXPORTER_OTLP_ENDPOINT",
            otel_cfg.get("exporter_otlp_endpoint", "http://localhost:4318/v1/traces"),
        ),
        exporter_otlp_headers=os.getenv(
            "EXPORTER_OTLP_HEADERS", otel_cfg.get("exporter_otlp_headers")
        ),
        console_export=console_export,
    )
    return AppConfig(
        environment=environment,
        logfire=logfire_config,
        sentry=sentry_config,
        otel=otel_config,
        mongo=UsageCollectionMongoConfig(
            database_name=os.getenv(
                "MONGO_DATABASE_NAME", mongo_cfg.get("database_name", "usage")
            ),
            collection_name=os.getenv(
                "MONGO_COLLECTION_NAME", mongo_cfg.get("collection_name", "ui_server")
            ),
            mongo_uri=os.getenv(
                "MONGO_URI",
                mongo_cfg.get("mongo_uri", "mongodb://admin:admin@localhost:27017"),
            ),
        ),
        smarty=SmartyConfig(
            base_url=os.getenv(
                "SMARTY_BASE_URL",
                smarty_cfg.get("base_url", "https://smarty.smartbank.uz"),
            ),
        ),
    )


config = New()

print("Config: ", config)
