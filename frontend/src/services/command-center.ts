import { apiRequest } from "./api-client";

export async function fetchLiveOverview() {
  return apiRequest<Record<string, unknown>>("/command-center/live-overview/");
}

export async function fetchThreatMap() {
  return apiRequest<Record<string, unknown>>("/command-center/threat-map/");
}

export async function fetchActiveIncidents() {
  return apiRequest<{ incidents: unknown[] }>("/command-center/active-incidents/");
}

export async function fetchEmergencyResponse() {
  return apiRequest<Record<string, unknown>>("/command-center/emergency-response/");
}

export async function fetchRegionalRisk() {
  return apiRequest<Record<string, unknown>>("/command-center/regional-risk/");
}

export async function fetchDashboardOverview() {
  return apiRequest<Record<string, unknown>>("/dashboard/overview/");
}

export async function fetchNationalSummary() {
  return apiRequest<Record<string, unknown>>("/analytics/national-summary/");
}

export async function fetchHeatmaps() {
  return apiRequest<Record<string, unknown>>("/analytics/heatmaps/");
}

export async function fetchMedicineFlow() {
  return apiRequest<Record<string, unknown>>("/analytics/medicine-flow/");
}

export async function fetchPendingApprovals() {
  return apiRequest<unknown[]>("/onboarding/");
}

export async function approveOnboarding(id: string) {
  return apiRequest(`/onboarding/${id}/approve/`, { method: "POST", body: "{}" });
}

export async function fetchAlerts() {
  return apiRequest<unknown[]>("/alerts/");
}
