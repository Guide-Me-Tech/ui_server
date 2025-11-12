# Metrics Prefix Changes Summary

## Overview
All telemetry metrics exported by the UI Server now start with the `ui_server` prefix to distinguish them from metrics of other services.

## Changes Made

### 1. Modified `telemetry/setup.py`
**Change**: Disabled automatic metrics from FastAPIInstrumentor

**Reason**: FastAPIInstrumentor automatically creates HTTP metrics with standard OpenTelemetry names (like `http.server.duration`, `http.server.active_requests`) that don't have the `ui_server` prefix. By disabling its metrics and using our custom MetricsCollector, we ensure all metrics have the proper prefix.

**Implementation**:
```python
FastAPIInstrumentor.instrument_app(
    app,
    excluded_urls="/health,/metrics",  # Don't trace health/metrics endpoints
    meter_provider=None,  # Disable automatic metrics (we use MetricsCollector instead)
)
```

### 2. Enhanced `telemetry/middleware.py`
**Change**: Integrated MetricsCollector into TelemetryMiddleware

**Reason**: The middleware now not only creates traces but also records metrics through MetricsCollector, which uses the `ui_server` prefix for all metrics.

**Key improvements**:
- Added `metrics_collector` parameter to constructor
- Records HTTP request metrics with `ui_server` prefix
- Tracks active requests counter
- Records request duration, status codes, and error rates
- All metrics go through MetricsCollector which has proper prefixes

### 3. Updated `src/server.py`
**Change**: Pass MetricsCollector instance to TelemetryMiddleware

**Implementation**:
```python
# Initialize metrics collector first
metrics_collector = MetricsCollector()

# Pass it to the middleware
app.add_middleware(TelemetryMiddleware, metrics_collector=metrics_collector)
```

## All Exported Metrics (with ui_server prefix)

### HTTP Request Metrics
- `ui_server.requests.total` - Total number of HTTP requests
- `ui_server.requests.duration` - Request duration histogram (milliseconds)
- `ui_server.requests.active` - Number of currently active requests
- `ui_server.errors.total` - Total number of HTTP errors (status >= 400)
- `ui_server.requests.language` - Request count by language

### Function Invocation Metrics
- `ui_server.functions.invocations` - Total function invocations
- `ui_server.functions.duration` - Function execution duration (milliseconds)
- `ui_server.functions.errors` - Total function errors

### Custom Metrics
- `ui_server.custom.{metric_name}` - Any custom metrics recorded via `record_custom_metric()`

## Metric Labels/Attributes

### Request Metrics Attributes
- `http.method` - HTTP method (GET, POST, etc.)
- `http.path` - Request path
- `http.status_code` - HTTP status code
- `language` - Request language (when provided)

### Function Metrics Attributes
- `function.name` - Name of the function invoked
- `function.version` - API version (v2, v3)
- `function.success` - Whether execution was successful

## Prometheus Format

When exported to Prometheus, metric names are converted:
- Dots (`.`) are replaced with underscores (`_`)
- Example: `ui_server.requests.total` → `ui_server_requests_total`

The Grafana dashboard (`grafana-dashboard.json`) is already configured to use these Prometheus-formatted names.

## Verification

To verify all metrics have the correct prefix:

1. Start the server
2. Make some requests
3. Access the `/metrics` endpoint
4. All metrics should start with `ui_server_` (Prometheus format)

Example output:
```
# HELP ui_server_requests_total Total number of requests
# TYPE ui_server_requests_total counter
ui_server_requests_total{http_method="GET",http_path="/health",http_status_code="200"} 5.0

# HELP ui_server_requests_duration Request duration in milliseconds
# TYPE ui_server_requests_duration histogram
ui_server_requests_duration_bucket{http_method="POST",http_path="/chat/v3/build_ui",http_status_code="200",le="10.0"} 2.0
...
```

## Impact

### Before Changes
- FastAPIInstrumentor created automatic metrics: `http.server.duration`, `http.server.active_requests`
- Custom metrics had `ui_server` prefix
- Mixed metric naming made it hard to filter by service

### After Changes
- **All metrics** exported start with `ui_server` prefix
- Easy to filter and query metrics for this service specifically
- No confusion with other services' metrics
- Consistent naming across all metrics

## No Breaking Changes

- The Grafana dashboard already uses the correct metric names
- Existing metric queries will continue to work
- All metric names that previously had `ui_server` prefix remain unchanged
- Only removed the automatic FastAPI metrics that didn't have the prefix

