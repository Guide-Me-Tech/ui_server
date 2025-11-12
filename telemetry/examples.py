"""
Example usage of telemetry decorators and manual instrumentation
"""

import asyncio
import time
from typing import Dict, List, Any
from telemetry.decorators import trace_function, trace_method
from telemetry import get_tracer, MetricsCollector


# Example 1: Simple function tracing
@trace_function()
async def fetch_user_data(user_id: str) -> Dict[str, Any]:
    """
    Fetch user data with automatic tracing
    """
    # Simulate database query
    await asyncio.sleep(0.1)
    return {"user_id": user_id, "name": "John Doe", "email": "john@example.com"}


# Example 2: Custom span name
@trace_function("process_payment_transaction")
async def process_payment(amount: float, user_id: str) -> bool:
    """
    Process payment with custom span name
    """
    # Simulate payment processing
    await asyncio.sleep(0.2)
    return True


# Example 3: Sync function tracing
@trace_function()
def calculate_discount(amount: float, discount_percentage: float) -> float:
    """
    Calculate discount (synchronous function)
    """
    return amount * (discount_percentage / 100)


# Example 4: Class with traced methods
class DataProcessor:
    """
    Example service class with traced methods
    """

    def __init__(self, metrics_collector: MetricsCollector):
        self.metrics_collector = metrics_collector
        self.tracer = get_tracer()

    @trace_method
    async def process_batch(self, items: List[Dict]) -> List[Dict]:
        """
        Process a batch of items with automatic tracing
        """
        results = []
        for item in items:
            result = await self._process_item(item)
            results.append(result)
        return results

    @trace_method
    async def _process_item(self, item: Dict) -> Dict:
        """
        Process a single item
        """
        await asyncio.sleep(0.05)
        return {"processed": True, **item}

    @trace_method
    def validate_input(self, data: Dict) -> bool:
        """
        Validate input data (synchronous)
        """
        required_fields = ["id", "type", "value"]
        return all(field in data for field in required_fields)


# Example 5: Manual instrumentation with custom attributes
async def complex_operation_with_manual_tracing(user_id: str, operation_type: str):
    """
    Example of manual tracing with custom attributes
    """
    tracer = get_tracer()
    metrics_collector = MetricsCollector()

    with tracer.start_as_current_span("complex_operation") as span:
        # Add custom attributes
        span.set_attribute("user_id", user_id)
        span.set_attribute("operation_type", operation_type)
        span.set_attribute("environment", "production")

        start_time = time.time()

        try:
            # Step 1: Fetch data
            with tracer.start_as_current_span("fetch_data") as fetch_span:
                fetch_span.set_attribute("data_source", "database")
                data = await fetch_user_data(user_id)
                fetch_span.set_attribute("data_size", len(data))

            # Step 2: Process data
            with tracer.start_as_current_span("transform_data") as transform_span:
                transform_span.set_attribute("transform_type", "normalization")
                # Simulate processing
                await asyncio.sleep(0.15)
                processed_data = {"processed": True, **data}

            # Step 3: Save results
            with tracer.start_as_current_span("save_results") as save_span:
                save_span.set_attribute("storage_type", "redis")
                await asyncio.sleep(0.1)
                save_span.set_attribute("records_saved", 1)

            duration_ms = (time.time() - start_time) * 1000

            # Record success metrics
            metrics_collector.record_custom_metric(
                metric_name="complex_operations",
                value=1,
                attributes={
                    "operation_type": operation_type,
                    "status": "success",
                    "user_id": user_id,
                },
            )

            span.set_attribute("success", True)
            span.set_attribute("duration_ms", duration_ms)

            return processed_data

        except Exception as e:
            # Record exception
            span.record_exception(e)
            span.set_attribute("success", False)
            span.set_attribute("error", str(e))

            # Record error metrics
            metrics_collector.record_custom_metric(
                metric_name="complex_operations",
                value=1,
                attributes={
                    "operation_type": operation_type,
                    "status": "error",
                    "error_type": type(e).__name__,
                },
            )

            raise


# Example 6: Nested spans with conditional logic
async def conditional_processing_example(data: Dict, use_cache: bool = True):
    """
    Example showing conditional tracing paths
    """
    tracer = get_tracer()

    with tracer.start_as_current_span("conditional_processing") as span:
        span.set_attribute("use_cache", use_cache)

        if use_cache:
            with tracer.start_as_current_span("check_cache") as cache_span:
                cache_span.set_attribute("cache_key", f"data_{data.get('id')}")
                # Simulate cache lookup
                await asyncio.sleep(0.01)
                cached_result = None  # Simulate cache miss

                if cached_result:
                    cache_span.set_attribute("cache_hit", True)
                    return cached_result
                else:
                    cache_span.set_attribute("cache_hit", False)

        # Process data if not cached
        with tracer.start_as_current_span("process_fresh_data") as process_span:
            process_span.set_attribute("data_id", data.get("id"))
            await asyncio.sleep(0.1)
            result = {"processed": True, **data}
            process_span.set_attribute("result_size", len(result))

        if use_cache:
            with tracer.start_as_current_span("update_cache") as update_span:
                update_span.set_attribute("cache_key", f"data_{data.get('id')}")
                await asyncio.sleep(0.01)

        return result


# Example 7: Error handling and recovery
@trace_function()
async def operation_with_retry(max_retries: int = 3):
    """
    Example of tracing operations with retry logic
    """
    tracer = get_tracer()

    for attempt in range(max_retries):
        with tracer.start_as_current_span(f"retry_attempt_{attempt + 1}") as span:
            span.set_attribute("attempt_number", attempt + 1)
            span.set_attribute("max_retries", max_retries)

            try:
                # Simulate operation that might fail
                await asyncio.sleep(0.05)

                # Simulate random failure (in real code, this would be actual logic)
                import random

                if random.random() < 0.3 and attempt < max_retries - 1:
                    raise ConnectionError("Temporary network error")

                span.set_attribute("success", True)
                return {"status": "success", "attempt": attempt + 1}

            except ConnectionError as e:
                span.record_exception(e)
                span.set_attribute("error", str(e))
                span.set_attribute("will_retry", attempt < max_retries - 1)

                if attempt < max_retries - 1:
                    # Wait before retry
                    backoff_time = 0.1 * (2**attempt)
                    await asyncio.sleep(backoff_time)
                    continue
                else:
                    raise


# Example 8: Parallel operations with tracing
async def parallel_operations_example(user_ids: List[str]):
    """
    Example of tracing parallel/concurrent operations
    """
    tracer = get_tracer()

    with tracer.start_as_current_span("parallel_processing") as span:
        span.set_attribute("user_count", len(user_ids))

        # Create tasks for parallel execution
        tasks = []
        for user_id in user_ids:
            # Each task will have its own span
            task = fetch_user_data(user_id)
            tasks.append(task)

        # Execute all tasks in parallel
        results = await asyncio.gather(*tasks)

        span.set_attribute("results_count", len(results))
        span.set_attribute("success", True)

        return results


# Example usage
async def main():
    """
    Main function to run examples
    """
    print("Running telemetry examples...")

    # Example 1: Simple function
    user_data = await fetch_user_data("user_123")
    print(f"User data: {user_data}")

    # Example 2: Custom span name
    payment_result = await process_payment(100.0, "user_123")
    print(f"Payment result: {payment_result}")

    # Example 3: Sync function
    discount = calculate_discount(100.0, 10.0)
    print(f"Discount: {discount}")

    # Example 4: Class methods
    metrics_collector = MetricsCollector()
    processor = DataProcessor(metrics_collector)
    items = [{"id": 1, "value": "test"}, {"id": 2, "value": "test2"}]
    results = await processor.process_batch(items)
    print(f"Processed: {len(results)} items")

    # Example 5: Manual tracing
    complex_result = await complex_operation_with_manual_tracing(
        "user_123", "data_sync"
    )
    print(f"Complex operation result: {complex_result}")

    # Example 6: Conditional processing
    conditional_result = await conditional_processing_example(
        {"id": "123", "value": "test"}, use_cache=True
    )
    print(f"Conditional result: {conditional_result}")

    # Example 7: Retry logic
    retry_result = await operation_with_retry(max_retries=3)
    print(f"Retry result: {retry_result}")

    # Example 8: Parallel operations
    user_ids = ["user_1", "user_2", "user_3"]
    parallel_results = await parallel_operations_example(user_ids)
    print(f"Parallel results: {len(parallel_results)} users fetched")

    print("All examples completed!")


if __name__ == "__main__":
    # Note: This is just for demonstration
    # In a real application, telemetry would be initialized in server.py
    asyncio.run(main())
