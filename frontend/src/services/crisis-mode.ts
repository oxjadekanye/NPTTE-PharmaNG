import { apiRequest } from "./api-client";

export async function fetchCrisisStatus() {
  return apiRequest<Record<string, unknown>>("/emergency-response/crisis-mode/");
}

export async function activateCrisis(scenario: string, targetStates?: string[]) {
  return apiRequest("/emergency-response/crisis-mode/activate/", {
    method: "POST",
    body: JSON.stringify({ scenario, target_states: targetStates ?? [] }),
  });
}
