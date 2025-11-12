"""
Telemetry decorators for easy instrumentation
"""

import time
from functools import wraps
from typing import Callable, Any
from opentelemetry import trace
from opentelemetry.trace import Status, StatusCode
from conf import logger


def trace_function(span_name: str | None = None):
    """
    Decorator to trace function execution

    Args:
        span_name: Optional custom span name. If not provided, uses function name.

    Usage:
        @trace_function()
        def my_function(arg1, arg2):
            # function code
            pass

        @trace_function("custom_operation")
        def another_function():
            # function code
            pass
    """

    def decorator(func: Callable) -> Callable:
        tracer = trace.get_tracer(__name__)
        name = span_name or f"{func.__module__}.{func.__name__}"

        @wraps(func)
        async def async_wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span(name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                start_time = time.time()
                try:
                    result = await func(*args, **kwargs)
                    duration = time.time() - start_time

                    span.set_attribute("function.duration_ms", duration * 1000)
                    span.set_status(Status(StatusCode.OK))

                    return result
                except Exception as e:
                    duration = time.time() - start_time

                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("function.duration_ms", duration * 1000)
                    span.set_attribute("function.error", str(e))

                    logger.error(
                        f"Function {func.__name__} failed",
                        error=str(e),
                        duration_ms=duration * 1000,
                    )

                    raise

        @wraps(func)
        def sync_wrapper(*args, **kwargs) -> Any:
            with tracer.start_as_current_span(name) as span:
                # Add function metadata
                span.set_attribute("function.name", func.__name__)
                span.set_attribute("function.module", func.__module__)

                start_time = time.time()
                try:
                    result = func(*args, **kwargs)
                    duration = time.time() - start_time

                    span.set_attribute("function.duration_ms", duration * 1000)
                    span.set_status(Status(StatusCode.OK))

                    return result
                except Exception as e:
                    duration = time.time() - start_time

                    span.record_exception(e)
                    span.set_status(Status(StatusCode.ERROR, str(e)))
                    span.set_attribute("function.duration_ms", duration * 1000)
                    span.set_attribute("function.error", str(e))

                    logger.error(
                        f"Function {func.__name__} failed",
                        error=str(e),
                        duration_ms=duration * 1000,
                    )

                    raise

        # Return appropriate wrapper based on function type
        if hasattr(func, "__code__") and func.__code__.co_flags & 0x80:
            # Async function
            return async_wrapper
        else:
            # Sync function
            return sync_wrapper

    return decorator


def trace_method(method: Callable) -> Callable:
    """
    Decorator to trace class method execution

    Usage:
        class MyClass:
            @trace_method
            def my_method(self, arg1):
                # method code
                pass
    """
    tracer = trace.get_tracer(__name__)

    @wraps(method)
    async def async_wrapper(self, *args, **kwargs) -> Any:
        span_name = f"{self.__class__.__name__}.{method.__name__}"

        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("class.name", self.__class__.__name__)
            span.set_attribute("method.name", method.__name__)

            start_time = time.time()
            try:
                result = await method(self, *args, **kwargs)
                duration = time.time() - start_time

                span.set_attribute("method.duration_ms", duration * 1000)
                span.set_status(Status(StatusCode.OK))

                return result
            except Exception as e:
                duration = time.time() - start_time

                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("method.duration_ms", duration * 1000)

                raise

    @wraps(method)
    def sync_wrapper(self, *args, **kwargs) -> Any:
        span_name = f"{self.__class__.__name__}.{method.__name__}"

        with tracer.start_as_current_span(span_name) as span:
            span.set_attribute("class.name", self.__class__.__name__)
            span.set_attribute("method.name", method.__name__)

            start_time = time.time()
            try:
                result = method(self, *args, **kwargs)
                duration = time.time() - start_time

                span.set_attribute("method.duration_ms", duration * 1000)
                span.set_status(Status(StatusCode.OK))

                return result
            except Exception as e:
                duration = time.time() - start_time

                span.record_exception(e)
                span.set_status(Status(StatusCode.ERROR, str(e)))
                span.set_attribute("method.duration_ms", duration * 1000)

                raise

    # Return appropriate wrapper based on method type
    if hasattr(method, "__code__") and method.__code__.co_flags & 0x80:
        return async_wrapper
    else:
        return sync_wrapper
