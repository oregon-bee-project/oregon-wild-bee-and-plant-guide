import logging
import os
import threading
import time
from contextlib import contextmanager

from fastapi import HTTPException

logger = logging.getLogger("bee_api.guardrails")

try:
    import psutil  # type: ignore
except Exception:  # pragma: no cover - optional dependency
    psutil = None


def _env_bool(name: str, default: bool) -> bool:
    raw = os.getenv(name)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


def _env_int(name: str, default: int, min_value: int = 1) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    return max(value, min_value)


class GuardrailSettings:
    def __init__(self) -> None:
        self.max_heavy_inflight = _env_int("MAX_HEAVY_INFLIGHT", 1, min_value=1)
        self.max_report_inflight = _env_int("MAX_REPORT_INFLIGHT", 1, min_value=1)
        self.max_export_inflight = _env_int("MAX_EXPORT_INFLIGHT", 1, min_value=1)
        self.memory_guard_enabled = _env_bool("MEMORY_GUARD_ENABLED", True)
        self.memory_usage_reject_pct = _env_int("MEMORY_USAGE_REJECT_PCT", 88, min_value=50)
        self.retry_after_seconds = _env_int("GUARDRAIL_RETRY_AFTER_SECONDS", 8, min_value=1)
        self.log_rejections = _env_bool("GUARDRAIL_LOG_REJECTIONS", True)


SETTINGS = GuardrailSettings()
_global_heavy_sem = threading.Semaphore(SETTINGS.max_heavy_inflight)
_report_sem = threading.Semaphore(SETTINGS.max_report_inflight)
_export_sem = threading.Semaphore(SETTINGS.max_export_inflight)
_lock = threading.Lock()
_inflight = {
    "global": 0,
    "report": 0,
    "export": 0,
}


def _reject(status_code: int, code: str, message: str) -> None:
    detail = {
        "code": code,
        "message": message,
        "retryAfterSeconds": SETTINGS.retry_after_seconds,
    }
    raise HTTPException(status_code=status_code, detail=detail)


def _memory_under_pressure() -> bool:
    if not SETTINGS.memory_guard_enabled:
        return False
    if psutil is None:
        return False
    try:
        used_pct = psutil.virtual_memory().percent
        return used_pct >= SETTINGS.memory_usage_reject_pct
    except Exception:
        return False


def _inc_counter(key: str) -> None:
    with _lock:
        _inflight[key] += 1


def _dec_counter(key: str) -> None:
    with _lock:
        _inflight[key] = max(0, _inflight[key] - 1)


@contextmanager
def heavy_request_guard(route_group: str):
    if route_group not in {"report", "export"}:
        raise ValueError("route_group must be 'report' or 'export'")

    sem = _report_sem if route_group == "report" else _export_sem
    start = time.perf_counter()

    if _memory_under_pressure():
        if SETTINGS.log_rejections:
            logger.warning("Guardrail rejected %s request due to memory pressure.", route_group)
        _reject(
            503,
            "MEMORY_PRESSURE",
            "The service is temporarily under memory pressure. Please retry shortly.",
        )

    if not _global_heavy_sem.acquire(blocking=False):
        if SETTINGS.log_rejections:
            logger.warning("Guardrail rejected %s request due to global saturation.", route_group)
        _reject(
            429,
            "TOO_MANY_HEAVY_REQUESTS",
            "The service is handling too many heavy requests right now. Please retry shortly.",
        )
    _inc_counter("global")

    acquired_local = sem.acquire(blocking=False)
    if not acquired_local:
        _global_heavy_sem.release()
        _dec_counter("global")
        if SETTINGS.log_rejections:
            logger.warning("Guardrail rejected %s request due to route saturation.", route_group)
        _reject(
            429,
            "TOO_MANY_ROUTE_REQUESTS",
            f"The {route_group} endpoint is busy. Please retry shortly.",
        )
    _inc_counter(route_group)

    try:
        yield
    finally:
        sem.release()
        _global_heavy_sem.release()
        _dec_counter(route_group)
        _dec_counter("global")
        elapsed_ms = round((time.perf_counter() - start) * 1000)
        logger.info("Completed %s request in %sms", route_group, elapsed_ms)
