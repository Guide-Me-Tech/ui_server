import os
import sys
import time
import logging
import functools
import psutil
import threading
from typing import Callable, Optional, Dict, Any, List, Union
from collections import defaultdict

"""
This module provides extensive performance metrics collection with a high degree of flexibility:
- Function execution times (count, total_time, max_time)
- Request counts
- Custom counters and gauges for arbitrary measurements
- System resource metrics (CPU, memory, optional disk, network)
- Control all behavior via environment variables, enabling or disabling features at runtime.
- Additional fine-grained variables for controlling logging format, how many metrics to store, and export endpoints.

By changing environment variables, developers, testers, ML engineers, and data scientists can tailor the metrics to their needs 
without code changes. The design aims to minimize overhead when disabled and provide deep insights when enabled.

Key environment variables:
- METRICS_ENABLED (true/false): Global toggle for all metrics.
- METRICS_LOG_LEVEL (e.g., DEBUG, INFO, WARN, ERROR): Controls verbosity of metric logs.
- METRICS_INTERVAL (int): Interval for system metrics collection in seconds.
- METRICS_SYSTEM_RESOURCES_ENABLED (true/false): Toggle system resource metrics.
- METRICS_DISK_ENABLED (true/false): If system metrics enabled, also track disk usage.
- METRICS_NETWORK_ENABLED (true/false): If system metrics enabled, also track network I/O.
- METRICS_JSON_LOGGING (true/false): If true, logs metrics in JSON format for easier machine parsing.
- METRICS_MAX_FUNCTIONS (int): Limit how many distinct functions metrics_data can store.
- METRICS_MAX_COUNTERS (int): Limit how many custom counters to store.
- METRICS_MAX_GAUGES (int): Limit how many custom gauges to store.
- METRICS_CUSTOM_EXPORT_ENABLE (true/false): If true, prepare data for custom export (e.g., HTTP POST to a monitoring server).
- METRICS_CUSTOM_EXPORT_ENDPOINT (string): Where to send metrics if METRICS_CUSTOM_EXPORT_ENABLE is true.
- METRICS_PROMETHEUS_EXPORT (true/false): If true, expose a Prometheus-compatible endpoint (integration outside this code).
- Additional variables can be introduced as needed without code changes, just reading env vars.

With these variables, we achieve extremely fine-grained control and maximum integrability.
"""

###########################
# Step 1: Environment Config
###########################
METRICS_ENABLED = os.environ.get("METRICS_ENABLED", "true").lower() == "true"
METRICS_LOG_LEVEL = os.environ.get("METRICS_LOG_LEVEL", "ERROR").upper()
METRICS_INTERVAL = int(os.environ.get("METRICS_INTERVAL", 60))
METRICS_SYSTEM_RESOURCES_ENABLED = (
    os.environ.get("METRICS_SYSTEM_RESOURCES_ENABLED", "true").lower() == "true"
)
METRICS_DISK_ENABLED = os.environ.get("METRICS_DISK_ENABLED", "false").lower() == "true"
METRICS_NETWORK_ENABLED = (
    os.environ.get("METRICS_NETWORK_ENABLED", "false").lower() == "true"
)
METRICS_JSON_LOGGING = os.environ.get("METRICS_JSON_LOGGING", "false").lower() == "true"
METRICS_MAX_FUNCTIONS = int(os.environ.get("METRICS_MAX_FUNCTIONS", 1000))
METRICS_MAX_COUNTERS = int(os.environ.get("METRICS_MAX_COUNTERS", 1000))
METRICS_MAX_GAUGES = int(os.environ.get("METRICS_MAX_GAUGES", 1000))

METRICS_CUSTOM_EXPORT_ENABLE = (
    os.environ.get("METRICS_CUSTOM_EXPORT_ENABLE", "false").lower() == "true"
)
METRICS_CUSTOM_EXPORT_ENDPOINT = os.environ.get("METRICS_CUSTOM_EXPORT_ENDPOINT", "")
METRICS_PROMETHEUS_EXPORT = (
    os.environ.get("METRICS_PROMETHEUS_EXPORT", "false").lower() == "true"
)

###########################
# Step 2: Logging Setup
###########################
logger = logging.getLogger(__name__)
logger.setLevel(logging.getLevelName(METRICS_LOG_LEVEL))
handler = logging.StreamHandler(sys.stdout)

if METRICS_JSON_LOGGING:
    # JSON format logging for easy machine parsing
    import json

    class JSONFormatter(logging.Formatter):
        def format(self, record):
            base = {
                "time": self.formatTime(record, self.datefmt),
                "level": record.levelname,
                "name": record.name,
                "message": record.getMessage(),
            }
            return json.dumps(base)

    handler.setFormatter(JSONFormatter())
else:
    handler.setFormatter(
        logging.Formatter("[%(asctime)s][%(levelname)s][%(name)s]: %(message)s")
    )

logger.addHandler(handler)

###########################
# Step 3: Metrics Storage
###########################
# Use dict with internal locks for thread-safety.
metrics_data: Dict[str, Any] = {
    "requests": 0,
    "function_calls": {},  # fname -> {count, total_time, max_time}
    "custom_counters": {},  # name -> int
    "custom_gauges": {},  # name -> float
    "system": {},
}
metrics_lock = threading.Lock()


###########################
# Step 4: Utility functions to ensure capacity limits
###########################
def ensure_capacity(dictionary: Dict, max_capacity: int):
    """
    Ensures that the given dictionary does not exceed max_capacity keys.
    If it does, remove oldest entries (or arbitrary entries) to avoid unbounded growth.
    This prevents unbounded memory usage if a large number of distinct keys appear.
    """
    if len(dictionary) > max_capacity:
        # Evict oldest entries. As dictionaries are insertion ordered in Python 3.7+,
        # we can pop from the beginning. If older Python, we may need an OrderedDict.
        # For simplicity, convert to a list and remove from start.
        # Here we just do a simple approach: pop items until capacity is met.
        excess = len(dictionary) - max_capacity
        keys_to_remove = list(dictionary.keys())[:excess]
        for k in keys_to_remove:
            del dictionary[k]


###########################
# Step 5: Decorator to measure function performance
###########################
def measure_performance(func: Callable):
    if not METRICS_ENABLED:
        return func

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        elapsed = time.perf_counter() - start

        with metrics_lock:
            fname = func.__name__
            fdata = metrics_data["function_calls"].get(
                fname, {"count": 0, "total_time": 0.0, "max_time": 0.0}
            )
            fdata["count"] += 1
            fdata["total_time"] += elapsed
            if elapsed > fdata["max_time"]:
                fdata["max_time"] = elapsed
            metrics_data["function_calls"][fname] = fdata

            # Ensure capacity
            ensure_capacity(metrics_data["function_calls"], METRICS_MAX_FUNCTIONS)

        logger.debug(f"Function {func.__name__} took {elapsed:.6f}s")
        return result

    return wrapper


###########################
# Step 6: Increment request count
###########################
def increment_request_count():
    if not METRICS_ENABLED:
        return
    with metrics_lock:
        metrics_data["requests"] += 1


###########################
# Step 7: Custom counters and gauges
###########################
def increment_counter(name: str, delta: int = 1):
    if not METRICS_ENABLED:
        return
    with metrics_lock:
        current_val = metrics_data["custom_counters"].get(name, 0)
        new_val = current_val + delta
        metrics_data["custom_counters"][name] = new_val
        ensure_capacity(metrics_data["custom_counters"], METRICS_MAX_COUNTERS)
    logger.debug(f"Counter {name} incremented by {delta}, new value={new_val}")


def set_gauge(name: str, value: float):
    if not METRICS_ENABLED:
        return
    with metrics_lock:
        metrics_data["custom_gauges"][name] = value
        ensure_capacity(metrics_data["custom_gauges"], METRICS_MAX_GAUGES)
    logger.debug(f"Gauge {name} set to {value}")


###########################
# Step 8: System metrics collection
###########################
_system_metrics_thread = None
_stop_system_metrics_thread = False


def _collect_system_metrics():
    while not _stop_system_metrics_thread:
        with metrics_lock:
            metrics_data["system"]["last_update"] = time.time()
            # CPU/Mem
            cpu_percent = psutil.cpu_percent(interval=None)
            mem_info = psutil.virtual_memory()
            metrics_data["system"]["cpu_percent"] = cpu_percent
            metrics_data["system"]["mem_used_mb"] = mem_info.used / (1024**2)
            metrics_data["system"]["mem_available_mb"] = mem_info.available / (1024**2)
            metrics_data["system"]["mem_total_mb"] = mem_info.total / (1024**2)

            if METRICS_DISK_ENABLED:
                # Collect disk usage for each partition
                disk_partitions = psutil.disk_partitions()
                disk_usage_data = {}
                for part in disk_partitions:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk_usage_data[part.mountpoint] = {
                        "total_mb": usage.total / (1024**2),
                        "used_mb": usage.used / (1024**2),
                        "free_mb": usage.free / (1024**2),
                        "percent": usage.percent,
                    }
                metrics_data["system"]["disk_usage"] = disk_usage_data

            if METRICS_NETWORK_ENABLED:
                net_io = psutil.net_io_counters()
                metrics_data["system"]["net_io"] = {
                    "bytes_sent_mb": net_io.bytes_sent / (1024**2),
                    "bytes_recv_mb": net_io.bytes_recv / (1024**2),
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout,
                }

            logger.debug("System metrics updated.")
        time.sleep(METRICS_INTERVAL)


def start_system_metrics_collection():
    global _system_metrics_thread
    if (
        METRICS_ENABLED
        and METRICS_SYSTEM_RESOURCES_ENABLED
        and _system_metrics_thread is None
    ):
        _system_metrics_thread = threading.Thread(
            target=_collect_system_metrics, daemon=True
        )
        _system_metrics_thread.start()
        logger.info("System resource metrics collection started.")


def stop_system_metrics_collection():
    global _stop_system_metrics_thread, _system_metrics_thread
    if _system_metrics_thread is not None:
        _stop_system_metrics_thread = True
        _system_metrics_thread.join()
        _system_metrics_thread = None
        logger.info("System resource metrics collection stopped.")


###########################
# Step 9: Snapshot and logging
###########################
def get_metrics_snapshot() -> Dict[str, Any]:
    if not METRICS_ENABLED:
        return {}
    with metrics_lock:
        snapshot = {
            "requests": metrics_data["requests"],
            "function_calls": {
                fname: dict(fdata)
                for fname, fdata in metrics_data["function_calls"].items()
            },
            "custom_counters": dict(metrics_data["custom_counters"]),
            "custom_gauges": dict(metrics_data["custom_gauges"]),
            "system": dict(metrics_data["system"])
            if METRICS_SYSTEM_RESOURCES_ENABLED
            else {},
        }
    return snapshot


def log_metrics_summary():
    if not METRICS_ENABLED:
        logger.debug("Metrics disabled, no summary.")
        return
    snapshot = get_metrics_snapshot()
    logger.info("Performance Metrics Summary:")
    logger.info(f"Total requests: {snapshot.get('requests', 0)}")

    func_calls = snapshot.get("function_calls", {})
    if func_calls:
        logger.info("Function Calls:")
        for fname, fdata in func_calls.items():
            count = fdata.get("count", 0)
            total_time = fdata.get("total_time", 0.0)
            max_time = fdata.get("max_time", 0.0)
            avg_time = (total_time / count) if count > 0 else 0.0
            logger.info(
                f"{fname}: calls={count}, total_time={total_time:.6f}s, avg_time={avg_time:.6f}s, max_time={max_time:.6f}s"
            )
    else:
        logger.info("No function calls recorded.")

    counters = snapshot.get("custom_counters", {})
    if counters:
        logger.info("Custom Counters:")
        for cname, cval in counters.items():
            logger.info(f"{cname}: {cval}")
    else:
        logger.info("No custom counters recorded.")

    gauges = snapshot.get("custom_gauges", {})
    if gauges:
        logger.info("Custom Gauges:")
        for gname, gval in gauges.items():
            logger.info(f"{gname}: {gval}")
    else:
        logger.info("No custom gauges recorded.")

    system_data = snapshot.get("system", {})
    if system_data:
        logger.info("System Resources:")
        logger.info(f"Updated at {system_data.get('last_update', 0)}")
        logger.info(
            f"CPU={system_data.get('cpu_percent', 0):.2f}% "
            f"Mem_Used={system_data.get('mem_used_mb', 0):.2f}MB "
            f"Mem_Available={system_data.get('mem_available_mb', 0):.2f}MB "
            f"Mem_Total={system_data.get('mem_total_mb', 0):.2f}MB"
        )

        if METRICS_DISK_ENABLED and "disk_usage" in system_data:
            logger.info("Disk Usage:")
            for mount, ddata in system_data["disk_usage"].items():
                logger.info(
                    f"{mount}: total={ddata['total_mb']:.2f}MB used={ddata['used_mb']:.2f}MB "
                    f"free={ddata['free_mb']:.2f}MB {ddata['percent']:.2f}%"
                )

        if METRICS_NETWORK_ENABLED and "net_io" in system_data:
            net_io = system_data["net_io"]
            logger.info("Network I/O:")
            logger.info(
                f"bytes_sent={net_io['bytes_sent_mb']:.2f}MB bytes_recv={net_io['bytes_recv_mb']:.2f}MB "
                f"packets_sent={net_io['packets_sent']} packets_recv={net_io['packets_recv']} "
                f"errin={net_io['errin']} errout={net_io['errout']} dropin={net_io['dropin']} dropout={net_io['dropout']}"
            )


###########################
# Step 10: Integrations for Custom Export
###########################
# If METRICS_CUSTOM_EXPORT_ENABLE = true and METRICS_CUSTOM_EXPORT_ENDPOINT is set,
# we could implement a function to POST metrics to that endpoint.
# This code just sketches out how you might do it.
# Real implementation would require requests or httpx library.

import json

try:
    import requests
except ImportError:
    requests = None


def export_metrics_custom():
    """
    Export metrics to a custom endpoint if enabled.
    This can be called periodically or after certain events.
    """
    if (
        not METRICS_ENABLED
        or not METRICS_CUSTOM_EXPORT_ENABLE
        or not METRICS_CUSTOM_EXPORT_ENDPOINT
    ):
        return
    if requests is None:
        logger.error("Requests library not installed, cannot export metrics.")
        return
    snapshot = get_metrics_snapshot()
    # Potentially sanitize or transform data for the endpoint
    # For now, just send JSON as is
    try:
        resp = requests.post(METRICS_CUSTOM_EXPORT_ENDPOINT, json=snapshot, timeout=10)
        if resp.status_code != 200:
            logger.warning(f"Metrics export returned status {resp.status_code}")
        else:
            logger.debug("Metrics successfully exported to custom endpoint.")
    except Exception as e:
        logger.error(f"Error exporting metrics: {e}", exc_info=True)


###########################
# Step 11: Start system metrics if enabled
###########################
_system_metrics_thread = None
_stop_system_metrics_thread = False


def _system_metrics_collector():
    while not _stop_system_metrics_thread:
        with metrics_lock:
            metrics_data["system"]["last_update"] = time.time()
            # CPU/Mem always collected if system resources enabled
            cpu_percent = psutil.cpu_percent(interval=None)
            mem_info = psutil.virtual_memory()
            metrics_data["system"]["cpu_percent"] = cpu_percent
            metrics_data["system"]["mem_used_mb"] = mem_info.used / (1024**2)
            metrics_data["system"]["mem_available_mb"] = mem_info.available / (1024**2)
            metrics_data["system"]["mem_total_mb"] = mem_info.total / (1024**2)

            if METRICS_DISK_ENABLED:
                disk_partitions = psutil.disk_partitions()
                disk_usage_data = {}
                for part in disk_partitions:
                    usage = psutil.disk_usage(part.mountpoint)
                    disk_usage_data[part.mountpoint] = {
                        "total_mb": usage.total / (1024**2),
                        "used_mb": usage.used / (1024**2),
                        "free_mb": usage.free / (1024**2),
                        "percent": usage.percent,
                    }
                metrics_data["system"]["disk_usage"] = disk_usage_data

            if METRICS_NETWORK_ENABLED:
                net_io = psutil.net_io_counters()
                metrics_data["system"]["net_io"] = {
                    "bytes_sent_mb": net_io.bytes_sent / (1024**2),
                    "bytes_recv_mb": net_io.bytes_recv / (1024**2),
                    "packets_sent": net_io.packets_sent,
                    "packets_recv": net_io.packets_recv,
                    "errin": net_io.errin,
                    "errout": net_io.errout,
                    "dropin": net_io.dropin,
                    "dropout": net_io.dropout,
                }

            logger.debug("System metrics updated.")
        time.sleep(METRICS_INTERVAL)


def start_system_metrics_collection():
    global _system_metrics_thread
    if (
        METRICS_ENABLED
        and METRICS_SYSTEM_RESOURCES_ENABLED
        and _system_metrics_thread is None
    ):
        _system_metrics_thread = threading.Thread(
            target=_system_metrics_collector, daemon=True
        )
        _system_metrics_thread.start()
        logger.info("System resource metrics collection started.")


if METRICS_ENABLED and METRICS_SYSTEM_RESOURCES_ENABLED:
    start_system_metrics_collection()

###########################
# Easy to modify by changing environment vars,
# and collects a wide range of metrics (functions, requests, counters/gauges, system resources, disk, network).
# We have also considered JSON logging, custom export endpoints, and maximum capacities.
###########################
