"""Local development settings."""
from .base import *  # noqa: F403

DEBUG = True

# Simpler static storage for local dev (no collectstatic required for admin)
STORAGES["staticfiles"]["BACKEND"] = (  # noqa: F405
    "django.contrib.staticfiles.storage.StaticFilesStorage"
)
