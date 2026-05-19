"""Assignable demo regulator staff for explorer workflows."""
from __future__ import annotations

from django.contrib.auth import get_user_model

from apps.operational_demo.constants import DEMO_TYPE

User = get_user_model()


def list_assignable_staff(*, limit: int = 50) -> list[dict]:
    qs = User.objects.filter(is_regulator=True, is_active=True).order_by("username")[:limit]
    out: list[dict] = []
    for u in qs:
        meta = u.metadata if isinstance(u.metadata, dict) else {}
        profile = meta.get("staff_profile") or {}
        if meta.get("demo_type") != DEMO_TYPE and not profile and not u.username.startswith("demo_staff"):
            if not u.is_superuser:
                continue
        active_tasks = u.assigned_operational_tasks.filter(task_status__in=["open", "in_progress"]).count()
        out.append(
            {
                "id": str(u.pk),
                "username": u.username,
                "full_name": profile.get("full_name") or u.get_full_name() or u.username,
                "role_title": profile.get("role_title", "Regulator officer"),
                "region_state": profile.get("region_state", ""),
                "team": profile.get("team", ""),
                "phone": profile.get("phone", u.phone_number or ""),
                "email": u.email,
                "specialisation": profile.get("specialisation", ""),
                "workload_count": active_tasks,
                "availability": profile.get("availability", "available"),
            }
        )
    return out
