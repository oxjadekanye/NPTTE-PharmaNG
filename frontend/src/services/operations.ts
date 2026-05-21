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

export async function fetchOverdueTasks() {
  return apiRequest<{ tasks: unknown[]; count: number }>("/operations/tasks/overdue/");
}

export async function fetchTaskCalendar(days = 30) {
  return apiRequest<{ calendar: unknown[]; count: number }>(
    `/operations/tasks/calendar/?days=${days}`
  );
}

export async function fetchFieldOperationsFeed() {
  return apiRequest<{ feed: unknown[]; count: number }>("/operations/field-operations/feed/");
}

export async function createOperationalTask(body: Record<string, unknown>) {
  return apiRequest("/operations/tasks/create/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function escalateTask(id: string, reason: string) {
  return apiRequest(`/operations/tasks/${id}/escalate/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export async function completeTaskWorkflow(id: string) {
  return apiRequest(`/operations/tasks/${id}/complete/`, { method: "POST" });
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
