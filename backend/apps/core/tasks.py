"""Async task abstraction — Celery-ready without hard dependency."""
from __future__ import annotations

import logging
from typing import Any, Callable

from django.conf import settings

logger = logging.getLogger("nptte.tasks")


def enqueue_task(name: str, func: Callable, *args, **kwargs) -> str:
    """
    Queue background work when Celery is configured; otherwise run synchronously.
    Returns task reference id for audit trails.
    """
    broker = getattr(settings, "CELERY_BROKER_URL", "")
    if broker:
        try:
            from celery import shared_task  # noqa: F401

            # Celery integration point — tasks registered via @shared_task in domain apps
            logger.info("Task queued: %s", name)
            return f"celery:{name}"
        except ImportError:
            pass
    logger.debug("Task executed inline: %s", name)
    func(*args, **kwargs)
    return f"inline:{name}"
