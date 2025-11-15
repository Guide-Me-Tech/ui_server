"""
Custom telemetry middleware for detailed request tracking
"""

import time
from typing import Callable, Optional
from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.types import ASGIApp
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from conf import logger, config
from telemetry.metrics import MetricsCollector


class TelemetryMiddleware(BaseHTTPMiddleware):
    """
    Middleware to add detailed telemetry for each request
    Tracks both traces and metrics with ui_server prefix
    """

    def __init__(
        self, app: ASGIApp, metrics_collector: Optional["MetricsCollector"] = None
    ):
        super().__init__(app)
        self.tracer = trace.get_tracer(__name__)
        self.metrics_collector = metrics_collector

    async def dispatch(self, request: Request, call_next: Callable) -> Response:
        """
        Process each request and add telemetry data
        Records both traces and metrics with ui_server prefix
        """
        start_time = time.time()

        # Increment active requests counter
        if self.metrics_collector:
            self.metrics_collector.increment_active_requests()

        # Create a span for this request
        with self.tracer.start_as_current_span(
            f"{request.method} {request.url.path}",
            kind=trace.SpanKind.SERVER,
        ) as span:
            # Add request attributes to span
            span.set_attribute("http.method", request.method)
            span.set_attribute("http.url", str(request.url))
            span.set_attribute("http.path", request.url.path)
            span.set_attribute("http.scheme", request.url.scheme)

            # Add custom headers as attributes
            language = None
            if "language" in request.headers:
                language = request.headers["language"]
                span.set_attribute("app.language", language)

            # Add client info
            if request.client:
                span.set_attribute("http.client_ip", request.client.host)

            try:
                # Process the request
                response = await call_next(request)

                # Calculate duration
                duration = time.time() - start_time
                duration_ms = duration * 1000

                # Add response attributes
                span.set_attribute("http.status_code", response.status_code)
                span.set_attribute("http.duration_ms", duration_ms)

                # Set span status based on response code
                if response.status_code >= 500:
                    span.set_status(Status(StatusCode.ERROR))
                elif response.status_code >= 400:
                    span.set_status(Status(StatusCode.ERROR))
                else:
                    span.set_status(Status(StatusCode.OK))

                # Record metrics with ui_server prefix
                if self.metrics_collector:
                    self.metrics_collector.record_request(
                        method=request.method,
                        path=request.url.path,
                        status_code=response.status_code,
                        duration_ms=duration_ms,
                        language=language,
                    )
                    self.metrics_collector.decrement_active_requests()

                # Log request details

                return response

            except Exception as e:
                # Record exception in span
                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))

                # Calculate duration
                duration = time.time() - start_time
                duration_ms = duration * 1000

                # Record error metrics
                if self.metrics_collector:
                    # Record as 500 error
                    self.metrics_collector.record_request(
                        method=request.method,
                        path=request.url.path,
                        status_code=500,
                        duration_ms=duration_ms,
                        language=language,
                    )
                    self.metrics_collector.decrement_active_requests()

                # Log error
                logger.error(
                    "Request failed",
                    method=request.method,
                    path=request.url.path,
                    error=str(e),
                    duration_ms=duration_ms,
                    trace_id=format(span.get_span_context().trace_id, "032x"),
                    span_id=format(span.get_span_context().span_id, "016x"),
                )

                raise
