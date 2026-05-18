import { apiRequest } from "./api-client";

export async function fetchEventReplay(params?: { since_sequence?: number; organisation_id?: string }) {
  const q = new URLSearchParams();
  if (params?.since_sequence) q.set("since_sequence", String(params.since_sequence));
  if (params?.organisation_id) q.set("organisation_id", params.organisation_id);
  const suffix = q.toString() ? `?${q}` : "";
  return apiRequest<{ events: unknown[]; count: number }>(`/streambus/replay/${suffix ? suffix : "/"}`);
}

export async function fetchCommandCenterLive(since = 0) {
  return apiRequest<{
    events: unknown[];
    escalations_open: number;
    pending_tasks: number;
    telemetry: Record<string, number>;
    live: boolean;
  }>(`/streambus/command-center/live/?since_sequence=${since}`);
}

export async function fetchLiveEscalations() {
  return apiRequest<{ escalations: unknown[] }>("/streambus/escalations/");
}

export async function fetchTelemetry() {
  return apiRequest<{ telemetry: unknown[] }>("/streambus/telemetry/");
}

export async function aggregateTelemetry(organisationId?: string) {
  return apiRequest("/streambus/telemetry/", {
    method: "POST",
    body: JSON.stringify({ organisation_id: organisationId }),
  });
}
