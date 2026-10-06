import os
import time
import uuid
import contextvars
import sys
from typing import Optional, Dict

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# Context variables to hold request-scoped state
_req_id: contextvars.ContextVar[Optional[str]] = contextvars.ContextVar("req_id", default=None)
_req_timings: contextvars.ContextVar[Dict[str, float]] = contextvars.ContextVar("req_timings", default={})
_req_start_time: contextvars.ContextVar[float] = contextvars.ContextVar("req_start_time", default=0.0)

def is_debug_enabled() -> bool:
    val = os.getenv("CLI_DEBUG", "false")
    if val is None:
        val = "false"
    return val.lower() in ("true", "1", "yes")

def init_request() -> str:
    """Initializes a new request context with a unique ID."""
    req_id = uuid.uuid4().hex[:4].upper()
    _req_id.set(req_id)
    _req_timings.set({})
    _req_start_time.set(time.perf_counter())
    return req_id

def get_req_id() -> str:
    req_id = _req_id.get()
    return f"[REQ {req_id}] " if req_id else ""

def log_header(title: str):
    if not is_debug_enabled():
        return
    print(f"\n────────────────────────────────────────────")
    print(f"{get_req_id()}{title}")
    print(f"────────────────────────────────────────────\n")

def log_stage(stage: str, message: str):
    if not is_debug_enabled():
        return
    print(f"{get_req_id()}[{stage}]\n→ {message}\n")

def log_info(stage: str, message: str):
    if not is_debug_enabled():
        return
    print(f"{get_req_id()}[{stage}]\n→ {message}")

def log_success(stage: str, message: str):
    if not is_debug_enabled():
        return
    print(f"{get_req_id()}[{stage}]\n✓ {message}\n")

def log_warning(stage: str, message: str):
    if not is_debug_enabled():
        return
    print(f"{get_req_id()}[{stage}]\n⚠ {message}\n")

def log_error(stage: str, message: str):
    if not is_debug_enabled():
        return
    print(f"{get_req_id()}[{stage}]\n✗ {message}\n")

def log_data(stage: str, data_lines: list):
    if not is_debug_enabled():
        return
    print(f"{get_req_id()}[{stage}]")
    for line in data_lines:
        print(f"{line}")
    print()

def start_timer(timer_name: str):
    if not is_debug_enabled():
        return
    timings = _req_timings.get()
    timings[f"{timer_name}_start"] = time.perf_counter()

def stop_timer(timer_name: str) -> float:
    if not is_debug_enabled():
        return 0.0
    timings = _req_timings.get()
    start = timings.get(f"{timer_name}_start", time.perf_counter())
    duration = time.perf_counter() - start
    timings[timer_name] = duration
    return duration

def log_all_timings():
    if not is_debug_enabled():
        return
    timings = _req_timings.get()
    total = time.perf_counter() - _req_start_time.get()
    
    print(f"{get_req_id()}[PERFORMANCE]")
    for key, duration in timings.items():
        if not key.endswith("_start"):
            print(f"→ {key.capitalize()}: {duration * 1000:.0f} ms")
    print(f"────────────────────")
    print(f"Total: {total * 1000:.0f} ms\n")
