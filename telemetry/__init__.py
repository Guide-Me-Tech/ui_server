"""
Telemetry module for UI Server
Provides OpenTelemetry instrumentation, metrics, and tracing
"""

from .setup import setup_telemetry, get_tracer, get_meter, get_prometheus_metrics
from .middleware import TelemetryMiddleware
from .metrics import MetricsCollector

__all__ = [
    "setup_telemetry",
    "get_tracer",
    "get_meter",
    "get_prometheus_metrics",
    "TelemetryMiddleware",
    "MetricsCollector",
]
