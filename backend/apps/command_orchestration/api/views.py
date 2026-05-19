"""Phase 20C — command orchestration APIs."""
from __future__ import annotations

from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView

from apps.command_orchestration.services.command_room import build_command_room_snapshot
from apps.command_orchestration.services.geospatial import build_map_markers, cluster_markers
from apps.command_orchestration.services.regional import build_regional_intelligence, list_regions
from apps.command_orchestration.services.tasks import build_task_orchestration_snapshot
from apps.core.api.responses import api_response
from apps.core.roles import is_regulator_user
from apps.enforcement.models import EnforcementCase
from apps.enforcement.services.investigation_room import (
    add_investigation_comment,
    add_investigation_note,
    build_investigation_room,
    transfer_assignment,
)


class RegulatorAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def _deny(self, request):
        if not (is_regulator_user(request.user) or request.user.is_superuser):
            return api_response(message="regulator_only", status_code=403)
        return None


class MapMarkersView(RegulatorAPIView):
    def get(self, request):
        denied = self._deny(request)
        if denied:
            return denied
        layer = request.GET.get("layer", "operational")
        cluster = request.GET.get("cluster", "1") in ("1", "true", "yes")
        limit = min(int(request.GET.get("limit", 120)), 250)
        payload = build_map_markers(layer=layer, limit=limit)
        if cluster and payload["markers"]:
            payload["markers"] = cluster_markers(payload["markers"])
            payload["clustered"] = True
        return api_response(data=payload, message="Map markers")


class RegionalListView(RegulatorAPIView):
    def get(self, request):
        denied = self._deny(request)
        if denied:
            return denied
        return api_response(data={"regions": list_regions()}, message="Regions")


class RegionalDetailView(RegulatorAPIView):
    def get(self, request, region_key: str):
        denied = self._deny(request)
        if denied:
            return denied
        intel = build_regional_intelligence(region_key)
        if not intel:
            return api_response(message="unknown_region", status_code=404)
        return api_response(data=intel, message="Regional intelligence")


class CommandRoomSnapshotView(RegulatorAPIView):
    def get(self, request):
        denied = self._deny(request)
        if denied:
            return denied
        return api_response(
            data=build_command_room_snapshot(request=request),
            message="Command room snapshot",
        )


class TaskOrchestrationView(RegulatorAPIView):
    def get(self, request):
        denied = self._deny(request)
        if denied:
            return denied
        return api_response(data=build_task_orchestration_snapshot(), message="Task orchestration")


class InvestigationRoomView(RegulatorAPIView):
    def get(self, request, case_id):
        denied = self._deny(request)
        if denied:
            return denied
        case = EnforcementCase.objects.filter(pk=case_id).first()
        if not case:
            return api_response(message="not_found", status_code=404)
        return api_response(data=build_investigation_room(case), message="Investigation room")

    def post(self, request, case_id):
        denied = self._deny(request)
        if denied:
            return denied
        case = EnforcementCase.objects.filter(pk=case_id).first()
        if not case:
            return api_response(message="not_found", status_code=404)
        action = (request.data.get("action") or "note").strip()
        if action == "note":
            note = add_investigation_note(
                case=case,
                author=request.user,
                body=request.data.get("body", ""),
                note_type=request.data.get("note_type", "general"),
                evidence_status=request.data.get("evidence_status", ""),
            )
            return api_response(data={"id": str(note.id)}, message="Note added", status_code=201)
        if action == "comment":
            comment = add_investigation_comment(
                case=case,
                author=request.user,
                body=request.data.get("body", ""),
                escalation_level=int(request.data.get("escalation_level", 0)),
            )
            return api_response(data={"id": str(comment.id)}, message="Comment added", status_code=201)
        if action == "transfer":
            from django.contrib.auth import get_user_model

            User = get_user_model()
            investigator = User.objects.get(pk=request.data["investigator_id"])
            transfer_assignment(
                case=case,
                investigator=investigator,
                actor=request.user,
                notes=request.data.get("notes", ""),
            )
            return api_response(message="Assignment transferred")
        return api_response(message="invalid_action", status_code=400)
