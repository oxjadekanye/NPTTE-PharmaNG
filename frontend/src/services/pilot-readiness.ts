import { apiRequest } from "./api-client";

export async function fetchPilotReadiness() {
  return apiRequest<Record<string, unknown>>("/pilot/readiness/");
}

export async function fetchOnboardingWorkflows() {
  return apiRequest<{ workflows: unknown[] }>("/pilot/onboarding-workflows/");
}

export async function fetchDemoControlInventory() {
  return apiRequest<Record<string, unknown>>("/pilot/demo-control/");
}

export async function runDemoControlAction(action: string) {
  return apiRequest("/pilot/demo-control/", {
    method: "POST",
    body: JSON.stringify({ action }),
  });
}

export async function fetchApiReadiness() {
  return apiRequest<Record<string, unknown>>("/pilot/api-readiness/");
}

export async function fetchSecurityReadiness() {
  return apiRequest<Record<string, unknown>>("/pilot/security/");
}

export async function fetchPerformanceReadiness() {
  return apiRequest<Record<string, unknown>>("/pilot/performance/");
}
