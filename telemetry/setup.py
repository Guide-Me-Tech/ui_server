"""
OpenTelemetry setup and configuration
"""

import os
from typing import Optional
from opentelemetry import trace, metrics
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor, ConsoleSpanExporter
from opentelemetry.sdk.metrics import MeterProvider
from opentelemetry.sdk.metrics.export import (
    PeriodicExportingMetricReader,
    ConsoleMetricExporter,
)
from opentelemetry.sdk.resources import (
    Resource,
    SERVICE_NAME,
    SERVICE_VERSION,
    DEPLOYMENT_ENVIRONMENT,
)
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.exporter.otlp.proto.http.trace_exporter import OTLPSpanExporter
from opentelemetry.exporter.prometheus import PrometheusMetricReader
from fastapi import FastAPI
from prometheus_client import generate_latest, REGISTRY
from conf import config

_tracer: Optional[trace.Tracer] = None
_meter: Optional[metrics.Meter] = None
_prometheus_reader: Optional[PrometheusMetricReader] = None


def setup_telemetry(
    app: FastAPI, service_name: str = "ui_server", version: str = "0"
) -> None:
    """
    Setup OpenTelemetry instrumentation for the FastAPI application

    Args:
        app: FastAPI application instance
        service_name: Name of the service
        version: Version of the service
    """
    global _tracer, _meter

    environment = config.environment

    # Create resource with service information
    resource = Resource(
        attributes={
            SERVICE_NAME: service_name,
            SERVICE_VERSION: version,
            DEPLOYMENT_ENVIRONMENT: environment,
        }
    )

    # Setup Tracing
    trace_provider = TracerProvider(resource=resource)

    # Configure exporters based on environment
    if config.otel.exporter_otlp_endpoint:
        # Use OTLP exporter if endpoint is configured
        otlp_trace_exporter = OTLPSpanExporter(
            endpoint=config.otel.exporter_otlp_endpoint,
            headers=_get_otel_headers(),
        )
        trace_provider.add_span_processor(BatchSpanProcessor(otlp_trace_exporter))

    # if environment == "development" or config.otel.console_export:
    #     # Add console exporter for development
    #     console_exporter = ConsoleSpanExporter()
    #     trace_provider.add_span_processor(BatchSpanProcessor(console_exporter))

    trace.set_tracer_provider(trace_provider)
    _tracer = trace.get_tracer(__name__)

    # Setup Metrics
    metric_readers = []

    # Use Prometheus scraping via /metrics endpoint (pull-based)
    global _prometheus_reader
    _prometheus_reader = PrometheusMetricReader()
    metric_readers.append(_prometheus_reader)

    if environment == "development" or config.otel.console_export:
        # Add console exporter for development
        console_metric_exporter = ConsoleMetricExporter()
        metric_readers.append(
            PeriodicExportingMetricReader(
                console_metric_exporter, export_interval_millis=60000
            )
        )

    meter_provider = MeterProvider(
        resource=resource,
        metric_readers=metric_readers,
    )
    metrics.set_meter_provider(meter_provider)
    _meter = metrics.get_meter(__name__)

    # Instrument FastAPI (traces only, not metrics)
    # We disable metrics here because we use custom MetricsCollector with ui_server prefix
    FastAPIInstrumentor.instrument_app(
        app,
        excluded_urls="/health,/metrics",  # Don't trace health/metrics endpoints
        meter_provider=None,  # Disable automatic metrics (we use MetricsCollector instead)
    )


def _get_otel_headers() -> dict:
    """Get OTLP headers from environment variables"""
    headers_str = config.otel.exporter_otlp_headers
    headers = {}

    if headers_str:
        for header in headers_str.split(","):
            if "=" in header:
                key, value = header.split("=", 1)
                headers[key.strip()] = value.strip()

    return headers


def get_tracer() -> trace.Tracer:
    """Get the global tracer instance"""
    if _tracer is None:
        return trace.get_tracer(__name__)
    return _tracer


def get_meter() -> metrics.Meter:
    """Get the global meter instance"""
    if _meter is None:
        return metrics.get_meter(__name__)
    return _meter


def get_prometheus_metrics() -> bytes:
    """
    Get metrics in Prometheus format for /metrics endpoint

    Returns:
        Metrics data in Prometheus text format
    """
    return generate_latest(REGISTRY)
