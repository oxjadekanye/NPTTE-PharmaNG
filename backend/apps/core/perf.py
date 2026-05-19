"""Development-only request timing (DEBUG or NPTTE_PERF_DEBUG=true)."""
from __future__ import annotations

import logging
import os
import time
from contextlib import contextmanager
from functools import wraps
from typing import Any, Callable

from django.conf import settings

logger = logging.getLogger("nptte.perf")


def perf_enabled() -> bool:
    if getattr(settings, "DEBUG", False):
        return True
    return os.environ.get("NPTTE_PERF_DEBUG", "").lower() in ("1", "true", "yes")


@contextmanager
def perf_span(label: str):
    if not perf_enabled():
        yield
        return
    start = time.perf_counter()
    try:
        yield
    finally:
        ms = (time.perf_counter() - start) * 1000
        logger.info("perf %s %.1fms", label, ms)


def perf_logged(label: str | None = None):
    def decorator(fn: Callable):
        name = label or fn.__qualname__

        @wraps(fn)
        def wrapper(*args: Any, **kwargs: Any):
            if not perf_enabled():
                return fn(*args, **kwargs)
            start = time.perf_counter()
            try:
                return fn(*args, **kwargs)
            finally:
                ms = (time.perf_counter() - start) * 1000
                logger.info("perf %s %.1fms", name, ms)

        return wrapper

    return decorator
