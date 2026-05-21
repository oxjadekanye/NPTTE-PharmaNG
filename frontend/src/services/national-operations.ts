import { apiRequest } from "./api-client";

export async function fetchNationalOperationsMetrics() {
  return apiRequest<Record<string, unknown>>("/intelligence/national-operations/");
}

export async function fetchAlertCenter(params?: { priority?: string; alert_type?: string }) {
  const q = new URLSearchParams();
  if (params?.priority) q.set("priority", params.priority);
  if (params?.alert_type) q.set("alert_type", params.alert_type);
  const suffix = q.toString() ? `?${q}` : "";
  return apiRequest<{
    alerts: unknown[];
    grouped: Record<string, unknown[]>;
    unread_count: number;
  }>(`/alerts/center/${suffix}`);
}
