"""
Custom metrics collection for business logic
"""

from typing import Dict, Any, Optional
from opentelemetry import metrics
from opentelemetry.metrics import Counter, Histogram, UpDownCounter
from conf import config


class MetricsCollector:
    """
    Centralized metrics collector for business metrics
    """

    def __init__(self, meter: Optional[metrics.Meter] = None):
        """
        Initialize metrics collector

        Args:
            meter: OpenTelemetry Meter instance
        """
        if meter is None:
            meter = metrics.get_meter(__name__)

        self.meter = meter

        # Request metrics
        self.request_counter = self.meter.create_counter(
            name="ui_server.requests.total",
            description="Total number of requests",
            unit="1",
        )

        self.request_duration = self.meter.create_histogram(
            name="ui_server.requests.duration",
            description="Request duration in milliseconds",
            unit="ms",
        )

        self.error_counter = self.meter.create_counter(
            name="ui_server.errors.total",
            description="Total number of errors",
            unit="1",
        )

        # Business metrics
        self.function_invocation_counter = self.meter.create_counter(
            name="ui_server.functions.invocations",
            description="Total number of function invocations",
            unit="1",
        )

        self.function_duration = self.meter.create_histogram(
            name="ui_server.functions.duration",
            description="Function execution duration in milliseconds",
            unit="ms",
        )

        self.function_error_counter = self.meter.create_counter(
            name="ui_server.functions.errors",
            description="Total number of function errors",
            unit="1",
        )

        # Active requests
        self.active_requests = self.meter.create_up_down_counter(
            name="ui_server.requests.active",
            description="Number of active requests",
            unit="1",
        )

        # Language distribution
        self.language_counter = self.meter.create_counter(
            name="ui_server.requests.language",
            description="Request count by language",
            unit="1",
        )

    def record_request(
        self,
        method: str,
        path: str,
        status_code: int,
        duration_ms: float,
        language: Optional[str] = None,
    ):
        """
        Record request metrics

        Args:
            method: HTTP method
            path: Request path
            status_code: HTTP status code
            duration_ms: Request duration in milliseconds
            language: Request language
        """
        attributes = {
            "http.method": method,
            "http.path": path,
            "http.status_code": status_code,
        }

        self.request_counter.add(1, attributes)
        self.request_duration.record(duration_ms, attributes)

        if status_code >= 400:
            self.error_counter.add(1, attributes)

        if language:
            self.language_counter.add(1, {"language": language})

    def record_function_invocation(
        self,
        function_name: str,
        duration_ms: float,
        success: bool,
        version: str = "v3",
    ):
        """
        Record function invocation metrics

        Args:
            function_name: Name of the function
            duration_ms: Function execution duration in milliseconds
            success: Whether the function execution was successful
            version: API version
        """
        attributes = {
            "function.name": function_name,
            "function.version": version,
            "function.success": success,
        }

        self.function_invocation_counter.add(1, attributes)
        self.function_duration.record(duration_ms, attributes)

        if not success:
            self.function_error_counter.add(1, attributes)

    def increment_active_requests(self, delta: int = 1):
        """Increment active request counter"""
        self.active_requests.add(delta)

    def decrement_active_requests(self, delta: int = 1):
        """Decrement active request counter"""
        self.active_requests.add(-delta)

    def record_custom_metric(
        self,
        metric_name: str,
        value: float,
        attributes: Optional[Dict[str, Any]] = None,
    ):
        """
        Record a custom metric

        Args:
            metric_name: Name of the metric
            value: Metric value
            attributes: Optional attributes for the metric
        """
        counter = self.meter.create_counter(
            name=f"ui_server.custom.{metric_name}",
            description=f"Custom metric: {metric_name}",
            unit="1",
        )
        counter.add(value, attributes or {})
