import { apiRequest } from "./api-client";

export type MapMarker = {
  id: string;
  lat: number;
  lng: number;
  layer: string;
  organisation: string;
  severity: string;
  status: string;
  risk_score: number;
  active_incidents?: number;
  assigned_officer?: string;
  explorer_entity_type?: string;
  explorer_entity_id?: string;
  title?: string;
  cluster?: boolean;
  count?: number;
};

export function fetchMapMarkers(layer: string, cluster = true) {
  return apiRequest<{ layer: string; markers: MapMarker[]; count: number; clustered?: boolean }>(
    `/command-orchestration/map-markers/?layer=${encodeURIComponent(layer)}&cluster=${cluster ? "1" : "0"}`
  );
}

export function fetchRegions() {
  return apiRequest<{ regions: { key: string; label: string; states: string[] }[] }>(
    "/command-orchestration/regions/"
  );
}

export function fetchRegionalIntelligence(regionKey: string) {
  return apiRequest<Record<string, unknown>>(`/command-orchestration/regions/${encodeURIComponent(regionKey)}/`);
}

export function fetchCommandRoomSnapshot() {
  return apiRequest<Record<string, unknown>>("/command-orchestration/command-room/");
}

export function fetchTaskOrchestration() {
  return apiRequest<Record<string, unknown>>("/command-orchestration/tasks/live/");
}

export function fetchInvestigationRoom(caseId: string) {
  return apiRequest<Record<string, unknown>>(`/command-orchestration/investigations/${caseId}/room/`);
}

export function postInvestigationRoom(
  caseId: string,
  body: { action: string; body?: string; note_type?: string; investigator_id?: string }
) {
  return apiRequest(`/command-orchestration/investigations/${caseId}/room/`, {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function fetchScopedStreamEvents(channel: string, since = 0) {
  return apiRequest<{ events: Record<string, unknown>[]; channel: string }>(
    `/streambus/scoped-replay/?channel=${encodeURIComponent(channel)}&since_sequence=${since}`
  );
}

export function copilotOperational(
  mode: string,
  body: { context_key?: string; entity_type?: string; entity_id?: string; user_question?: string }
) {
  const path =
    mode === "operational_recommendations"
      ? "recommend-actions/"
      : mode === "escalation_reasoning"
        ? "recommend-actions/"
        : "recommend-actions/";
  return apiRequest(`/copilot/${path}`, {
    method: "POST",
    body: JSON.stringify({ ...body, prompt_mode: mode }),
  });
}
