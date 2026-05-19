"""Load tenant-safe explorer context for copilot prompts."""
from __future__ import annotations

from apps.explorer.api.views import _check_explorer_access
from apps.explorer.constants import AGGREGATE_IDS
from apps.explorer.services.context_router import resolve_context_route
from apps.explorer.services.context_summary import build_light_overview
from apps.explorer.services.payloads import build_explorer_bundle
from apps.explorer.services.quick_explorer import build_quick_bundle


def resolve_copilot_target(
    *,
    request,
    entity_type: str | None = None,
    entity_id: str | None = None,
    context_key: str | None = None,
) -> tuple[bool, str, str, str]:
    """Returns ok, reason, entity_type, entity_id."""
    if context_key:
        route = resolve_context_route(context_key=context_key, user=request.user)
        et, eid = route["entity_type"], route["entity_id"]
        ok, reason = _check_explorer_access(request, et, eid)
        return ok, reason, et, eid

    if not entity_type or not entity_id:
        return False, "entity_or_context_required", "", ""

    ok, reason = _check_explorer_access(request, entity_type, entity_id)
    return ok, reason, entity_type, entity_id


def load_explorer_bundle(
    *,
    request,
    entity_type: str,
    entity_id: str,
    context_key: str | None = None,
    selected_record_ids: list[str] | None = None,
) -> dict:
    if context_key:
        bundle = build_quick_bundle(context_key=context_key, request=request, page=1, page_size=25)
    elif entity_id in AGGREGATE_IDS:
        bundle = build_light_overview(request, entity_type, entity_id)
    else:
        bundle = build_explorer_bundle(request, entity_type, entity_id)

    if selected_record_ids:
        from apps.copilot.services.source_records import _record_list

        rows = _record_list(bundle)
        wanted = {str(x) for x in selected_record_ids}
        filtered = [r for r in rows if str(r.get("id", "")) in wanted]
        bundle = {**bundle, "records": filtered, "record_count": len(filtered)}

    bundle.setdefault("entity_type", entity_type)
    bundle.setdefault("entity_id", entity_id)
    if context_key:
        bundle["context_key"] = context_key
    return bundle
