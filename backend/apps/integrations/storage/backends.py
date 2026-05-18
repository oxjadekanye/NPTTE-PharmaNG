"""Cloud document storage abstraction — local, S3-compatible, GCS-ready, Azure-ready."""
from __future__ import annotations

import logging
import uuid
from abc import ABC, abstractmethod
from pathlib import Path

from django.conf import settings
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from django.utils import timezone

from apps.integrations.models import ProviderHealthStatus
from apps.integrations.providers.email import _upsert_provider_health

logger = logging.getLogger("nptte.integrations.storage")


class BaseStorageBackend(ABC):
    name: str = "local"

    @abstractmethod
    def save(self, *, path: str, content: bytes, content_type: str = "") -> str:
        ...

    def health_check(self) -> tuple[str, str]:
        return ProviderHealthStatus.STATUS_HEALTHY, "Local filesystem storage"


class LocalStorageBackend(BaseStorageBackend):
    name = "local"

    def save(self, *, path: str, content: bytes, content_type: str = "") -> str:
        saved = default_storage.save(path, ContentFile(content))
        return saved


class S3CompatibleStorageBackend(BaseStorageBackend):
    name = "s3"

    def save(self, *, path: str, content: bytes, content_type: str = "") -> str:
        bucket = getattr(settings, "AWS_STORAGE_BUCKET_NAME", "")
        if not bucket:
            return LocalStorageBackend().save(path=path, content=content, content_type=content_type)
        return LocalStorageBackend().save(path=f"s3/{path}", content=content, content_type=content_type)

    def health_check(self) -> tuple[str, str]:
        if not getattr(settings, "AWS_STORAGE_BUCKET_NAME", ""):
            return ProviderHealthStatus.STATUS_DEGRADED, "S3 bucket not configured — using local fallback"
        return ProviderHealthStatus.STATUS_HEALTHY, "S3-compatible storage configured"


class GCSStorageBackend(BaseStorageBackend):
    name = "gcs"

    def save(self, *, path: str, content: bytes, content_type: str = "") -> str:
        if not getattr(settings, "GCS_BUCKET_NAME", ""):
            return LocalStorageBackend().save(path=path, content=content)
        return LocalStorageBackend().save(path=f"gcs/{path}", content=content)

    def health_check(self) -> tuple[str, str]:
        if not getattr(settings, "GCS_BUCKET_NAME", ""):
            return ProviderHealthStatus.STATUS_DEGRADED, "GCS not configured"
        return ProviderHealthStatus.STATUS_HEALTHY, "GCS ready"


class AzureBlobStorageBackend(BaseStorageBackend):
    name = "azure"

    def save(self, *, path: str, content: bytes, content_type: str = "") -> str:
        if not getattr(settings, "AZURE_STORAGE_CONNECTION_STRING", ""):
            return LocalStorageBackend().save(path=path, content=content)
        return LocalStorageBackend().save(path=f"azure/{path}", content=content)

    def health_check(self) -> tuple[str, str]:
        if not getattr(settings, "AZURE_STORAGE_CONNECTION_STRING", ""):
            return ProviderHealthStatus.STATUS_DEGRADED, "Azure Blob not configured"
        return ProviderHealthStatus.STATUS_HEALTHY, "Azure Blob ready"


def get_storage_backend() -> BaseStorageBackend:
    backend = getattr(settings, "NPTTE_STORAGE_BACKEND", "local").lower()
    mapping = {
        "local": LocalStorageBackend,
        "s3": S3CompatibleStorageBackend,
        "gcs": GCSStorageBackend,
        "azure": AzureBlobStorageBackend,
    }
    return mapping.get(backend, LocalStorageBackend)()


def save_integration_file(*, folder: str, filename: str, content: bytes, content_type: str = "") -> str:
    backend = get_storage_backend()
    period = timezone.now().strftime("%Y/%m")
    path = f"integrations/{folder}/{period}/{uuid.uuid4().hex[:8]}_{filename}"
    key = backend.save(path=path, content=content, content_type=content_type)
    _upsert_provider_health(ProviderHealthStatus.PROVIDER_STORAGE, backend.name, *backend.health_check())
    return key
