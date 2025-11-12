# Telemetry Architecture

This document describes the architecture and data flow of the UI Server telemetry system.

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         UI Server                                │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐  │
│  │                    FastAPI Application                    │  │
│  │                                                            │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │           TelemetryMiddleware                     │   │  │
│  │  │  • Intercepts all HTTP requests                  │   │  │
│  │  │  • Creates span for each request                 │   │  │
│  │  │  • Adds HTTP attributes                          │   │  │
│  │  │  • Measures duration                             │   │  │
│  │  │  • Records exceptions                            │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                          ↓                               │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │           Endpoint Handlers                       │   │  │
│  │  │  • /chat/v3/build_ui                             │   │  │
│  │  │  • /chat/v2/build_ui/actions                     │   │  │
│  │  │  • Manual span creation                          │   │  │
│  │  │  • Function metrics recording                    │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  │                          ↓                               │  │
│  │  ┌──────────────────────────────────────────────────┐   │  │
│  │  │         Business Logic (functions_mapper)         │   │  │
│  │  │  • User code with @trace_function decorators     │   │  │
│  │  │  • Manual tracer.start_as_current_span()         │   │  │
│  │  │  • Custom attributes and metrics                 │   │  │
│  │  └──────────────────────────────────────────────────┘   │  │
│  └────────────────────────────────────────────────────────┘  │
│                                                               │
│  ┌────────────────────┐  ┌──────────────────────────────┐   │
│  │  MetricsCollector  │  │  OpenTelemetry Tracer        │   │
│  │  • Request metrics │  │  • Span creation             │   │
│  │  • Function metrics│  │  • Context propagation       │   │
│  │  • Custom metrics  │  │  • Attribute management      │   │
│  └────────────────────┘  └──────────────────────────────┘   │
│           ↓                          ↓                        │
│  ┌────────────────────────────────────────────────────────┐  │
│  │            OpenTelemetry SDK                           │  │
│  │  • BatchSpanProcessor                                  │  │
│  │  • PeriodicExportingMetricReader                       │  │
│  │  • Resource management                                 │  │
│  └────────────────────────────────────────────────────────┘  │
│           ↓                          ↓                        │
│  ┌────────────────────┐  ┌──────────────────────────────┐   │
│  │  OTLP Exporter     │  │  Console Exporter (dev)      │   │
│  │  (Production)      │  │  (Development)               │   │
│  └────────────────────┘  └──────────────────────────────┘   │
└───────────────┬──────────────────────┬───────────────────────┘
                │                      │
                ↓                      ↓
    ┌─────────────────────┐   ┌──────────────────┐
    │  Observability      │   │  Console Output  │
    │  Platform           │   │  (stdout/stderr) │
    │                     │   └──────────────────┘
    │  • Jaeger           │
    │  • Grafana Cloud    │
    │  • New Relic        │
    │  • Honeycomb        │
    │  • Datadog          │
    │  • AWS X-Ray        │
    └─────────────────────┘
```

## Data Flow

### Request Processing Flow

```
1. HTTP Request arrives
   ↓
2. TelemetryMiddleware intercepts
   ↓
3. Create parent span: "GET /path"
   ↓
4. Add HTTP attributes (method, path, client_ip, etc.)
   ↓
5. FastAPI routes to endpoint handler
   ↓
6. Endpoint creates child span: "build_ui_v3"
   ↓
7. Add function attributes (name, version, language)
   ↓
8. Call business logic from functions_mapper
   ↓
9. [Optional] Business logic creates more child spans
   ↓
10. Function completes, record duration
    ↓
11. MetricsCollector records metrics
    ↓
12. Return response
    ↓
13. TelemetryMiddleware adds response attributes
    ↓
14. Span completed with final duration
    ↓
15. BatchSpanProcessor batches span
    ↓
16. OTLP Exporter sends to observability platform
```

### Span Hierarchy Example

```
HTTP Request Span (root)
└─ build_ui_v3 (child)
   ├─ fetch_user_data (child)
   ├─ process_data (child)
   │  ├─ validate_input (grandchild)
   │  └─ transform_data (grandchild)
   └─ save_results (child)
```

## Component Details

### 1. Setup Module (`setup.py`)

**Responsibilities:**
- Initialize OpenTelemetry SDK
- Configure trace provider and meter provider
- Set up exporters (OTLP, Console)
- Manage resource attributes
- Provide global tracer and meter instances

**Key Functions:**
- `setup_telemetry(app, service_name, version)` - Initialize everything
- `get_tracer()` - Get global tracer instance
- `get_meter()` - Get global meter instance

### 2. Middleware (`middleware.py`)

**Responsibilities:**
- Intercept all HTTP requests
- Create and manage request spans
- Record HTTP request metrics via MetricsCollector
- Add HTTP-specific attributes
- Measure request duration
- Track active requests
- Handle exceptions gracefully

**Attributes Added:**
- `http.method` - HTTP method
- `http.url` - Full URL
- `http.path` - Request path
- `http.status_code` - Response status
- `http.duration_ms` - Request duration
- `http.client_ip` - Client IP address
- `app.language` - Request language header

**Metrics Recorded:**
- All HTTP request metrics through MetricsCollector
- Ensures all metrics have `ui_server` prefix

### 3. Metrics Collector (`metrics.py`)

**Responsibilities:**
- Define standard metrics
- Record request metrics
- Record function invocation metrics
- Support custom business metrics
- Track active requests

**Metrics Provided:**
- `ui_server.requests.total` - Counter
- `ui_server.requests.duration` - Histogram
- `ui_server.requests.active` - UpDownCounter
- `ui_server.errors.total` - Counter
- `ui_server.functions.invocations` - Counter
- `ui_server.functions.duration` - Histogram
- `ui_server.functions.errors` - Counter
- `ui_server.requests.language` - Counter

### 4. Decorators (`decorators.py`)

**Responsibilities:**
- Provide easy-to-use function tracing
- Support both sync and async functions
- Add function metadata to spans
- Handle exceptions properly

**Decorators Provided:**
- `@trace_function(span_name=None)` - Trace any function
- `@trace_method` - Trace class methods

## Configuration

### Environment Variables

| Variable | Purpose | Default | Example |
|----------|---------|---------|---------|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | OTLP endpoint URL | None | `http://localhost:4317` |
| `OTEL_EXPORTER_OTLP_HEADERS` | Authentication headers | None | `authorization=Bearer TOKEN` |
| `OTEL_CONSOLE_EXPORT` | Enable console export | `false` | `true` |
| `ENVIRONMENT` | Deployment environment | `development` | `production` |

### Resource Attributes

Automatically added to all spans and metrics:
- `service.name` - Service name (ui_server)
- `service.version` - Service version (from version.txt)
- `deployment.environment` - Environment (development/production)

## Export Strategies

### Development Mode
```
TracerProvider
└─ BatchSpanProcessor
   └─ ConsoleSpanExporter → stdout

MeterProvider
└─ PeriodicExportingMetricReader (60s)
   └─ ConsoleMetricExporter → stdout
```

### Production Mode
```
TracerProvider
└─ BatchSpanProcessor
   └─ OTLPSpanExporter → OTLP Endpoint

MeterProvider
└─ PeriodicExportingMetricReader (60s)
   └─ OTLPMetricExporter → OTLP Endpoint
```

### Hybrid Mode (Both)
```
TracerProvider
├─ BatchSpanProcessor → OTLPSpanExporter
└─ BatchSpanProcessor → ConsoleSpanExporter

MeterProvider
├─ PeriodicExportingMetricReader → OTLPMetricExporter
└─ PeriodicExportingMetricReader → ConsoleMetricExporter
```

## Performance Considerations

### Batching
- Spans are batched before export
- Default batch size: 512 spans
- Max queue size: 2048 spans
- Export interval: 5 seconds

### Async Export
- All exports happen in background threads
- No blocking of main application
- Failed exports are retried

### Sampling (Future)
- Can implement sampling for high-volume endpoints
- TraceIDRatioBased sampler
- ParentBased sampler

### Resource Usage
- Minimal CPU overhead (~1-2%)
- Memory scales with request volume
- Network bandwidth depends on trace volume

## Error Handling

### Graceful Degradation
- If OTLP endpoint is unavailable, traces are dropped
- Console exporter always works (no network dependency)
- Application continues to function normally

### Exception Recording
- Exceptions are automatically recorded in spans
- Stack traces are included
- Error status is set on span

## Security Considerations

### Data Protection
- Sensitive data should NOT be added to span attributes
- Review all custom attributes
- Use environment variables for credentials

### Authentication
- OTLP headers can include authentication
- Support for Bearer tokens, API keys
- TLS/SSL for encrypted transmission

## Future Enhancements

### Planned Features
1. **Prometheus Metrics Export**
   - Add `/metrics` endpoint
   - Export metrics in Prometheus format

2. **Automatic Sampling**
   - Sample high-volume endpoints
   - Keep all error traces

3. **Custom Dashboard Templates**
   - Pre-built Grafana dashboards
   - Alert rule templates

4. **Distributed Context Propagation**
   - Propagate trace context to external services
   - Support W3C Trace Context standard

5. **Log Correlation**
   - Add trace IDs to log messages
   - Link traces to logs in observability platforms

## Integration Examples

### Adding Tracing to a New Endpoint

```python
@app.post("/new/endpoint")
async def new_endpoint(request: Request, data: InputData):
    with tracer.start_as_current_span("new_endpoint_operation") as span:
        # Add attributes
        span.set_attribute("data.type", data.type)
        span.set_attribute("data.size", len(data.items))
        
        # Your logic here
        result = process_data(data)
        
        # Record metrics
        metrics_collector.record_custom_metric(
            "new_endpoint_calls",
            1,
            {"status": "success"}
        )
        
        return result
```

### Adding Tracing to Business Logic

```python
@trace_function("process_user_request")
async def process_user_request(user_id: str, request_data: dict):
    # Automatically traced
    # Add custom attributes in the function
    tracer = get_tracer()
    span = trace.get_current_span()
    span.set_attribute("user_id", user_id)
    
    # Your logic here
    return result
```

## Monitoring the Telemetry System

### Health Checks
- Monitor OTLP exporter success rate
- Check span queue size
- Monitor export latency

### Metrics to Watch
- `otel.exporter.spans.exported` - Exported span count
- `otel.exporter.spans.dropped` - Dropped span count
- `otel.processor.queue_size` - Current queue size

## References

- [OpenTelemetry Specification](https://opentelemetry.io/docs/specs/otel/)
- [Python SDK Documentation](https://opentelemetry-python.readthedocs.io/)
- [OTLP Protocol](https://opentelemetry.io/docs/specs/otlp/)

