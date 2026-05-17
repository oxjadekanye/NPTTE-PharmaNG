"""
User and role models for NPTTE platform identity.
"""
from __future__ import annotations
from django.contrib.auth.models import AbstractUser
from django.db import models

from apps.core.constants import RecordStatus
from apps.core.models import MetadataModel, TimestampedModel, UUIDPrimaryKeyModel
from apps.core.roles import sync_regulator_flag


class Role(UUIDPrimaryKeyModel, TimestampedModel, MetadataModel):
    """
    Platform role definition (e.g. regulator inspector, pharmacy dispenser).

    Assigned to users; organisation-scoped permissions are layered in later phases.
    """

    code = models.CharField(max_length=64, unique=True, db_index=True)
    name = models.CharField(max_length=128)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)

    class Meta:
        ordering = ["name"]
        verbose_name = "Role"
        verbose_name_plural = "Roles"

    def __str__(self):
        return self.name


class User(UUIDPrimaryKeyModel, AbstractUser, MetadataModel):
    """
    Custom user model for NPTTE.

    Extends Django auth with national ID reference, phone contact, and role linkage.
    Organisation membership is managed via organisations app in later phases.
    """

    phone_number = models.CharField(max_length=32, blank=True, db_index=True)
    national_id_number = models.CharField(
        max_length=64,
        blank=True,
        db_index=True,
        help_text="National identification reference (e.g. NIN) where applicable.",
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="users",
    )
    organisation = models.ForeignKey(
        "organisations.Organisation",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="members",
        help_text="Primary organisation membership for supply chain and pharmacy users.",
    )
    is_regulator = models.BooleanField(
        default=False,
        help_text="Quick flag for regulator-facing access; refined via RBAC later.",
    )
    status = models.CharField(
        max_length=32,
        choices=RecordStatus.CHOICES,
        default=RecordStatus.ACTIVE,
        db_index=True,
    )

    class Meta:
        ordering = ["username"]
        verbose_name = "User"
        verbose_name_plural = "Users"

    def save(self, *args, **kwargs):
        sync_regulator_flag(self)
        super().save(*args, **kwargs)

    @property
    def role_code(self) -> str | None:
        return self.role.code if self.role_id and self.role else None

    def __str__(self):
        return self.get_full_name() or self.username
