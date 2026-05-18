import { apiRequest } from "./api-client";

export async function fetchTenantContext() {
  return apiRequest<{
    active_organisation_id: string;
    membership_organisation_ids: string[];
  }>("/tenancy/context/current/");
}

export async function switchOrganisationContext(organisationId: string, reason = "regulator_review") {
  return apiRequest("/tenancy/context/switch/", {
    method: "POST",
    body: JSON.stringify({ organisation_id: organisationId, reason }),
  });
}

export async function fetchOrganisationDashboard() {
  return apiRequest<Record<string, unknown>>("/tenancy/dashboard/");
}

export async function applyOrganisationOnboarding(payload: Record<string, string>) {
  return apiRequest("/tenancy/onboarding/apply/", {
    method: "POST",
    body: JSON.stringify(payload),
    auth: false,
  });
}

export async function fetchApprovalQueue() {
  return apiRequest<{ queue: unknown[] }>("/tenancy/regulator/approval-queue/");
}
