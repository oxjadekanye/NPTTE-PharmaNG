import { apiRequest } from "./api-client";

export async function fetchWorkflowTimeline() {
  return apiRequest<{ timeline: unknown[]; count: number }>("/operations/workflow/timeline/");
}

export async function fetchActivityFeed() {
  return apiRequest<{ feed: unknown[]; count: number }>("/operations/activity/feed/");
}

export async function fetchOperationalTasks(status?: string) {
  const q = status ? `?status=${encodeURIComponent(status)}` : "";
  return apiRequest<{ tasks: unknown[]; count: number }>(`/operations/tasks/${q}`);
}

export async function fetchRegulatorHistory() {
  return apiRequest<{ history: unknown[]; count: number }>("/operations/regulator/history/");
}

export async function fetchOrganisationSettings(organisationId?: string) {
  const q = organisationId ? `?organisation_id=${organisationId}` : "";
  return apiRequest<Record<string, unknown>>(`/operations/organisation/settings/${q}`);
}

export async function fetchNotificationUnread() {
  return apiRequest<{ unread: number }>("/notifications/unread/");
}
