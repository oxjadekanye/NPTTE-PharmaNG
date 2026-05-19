import { apiRequest } from "./api-client";

export async function fetchNationalRisk() {
  return apiRequest<Record<string, unknown>>("/intelligence/national-risk/");
}

export async function fetchRegionalRisk(state?: string) {
  const q = state ? `?state=${encodeURIComponent(state)}` : "";
  return apiRequest("/intelligence/regional-risk/" + q);
}

export async function fetchProductRisk() {
  return apiRequest<{ products: unknown[] }>("/intelligence/product-risk/");
}

export async function fetchOrganisationRisk(organisationId: string) {
  return apiRequest(`/intelligence/organisation-risk/?organisation_id=${organisationId}`);
}

export async function fetchIntelligenceSignals() {
  return apiRequest<{ signals: unknown[] }>("/intelligence/signals/");
}

export async function fetchCounterfeitClusters() {
  return apiRequest<{ clusters: unknown[] }>("/intelligence/clusters/");
}

export async function runCorrelation() {
  return apiRequest("/intelligence/run-correlation/", { method: "POST", body: JSON.stringify({}) });
}

export async function fetchNarratives(type?: string) {
  const q = type ? `?type=${encodeURIComponent(type)}` : "";
  return apiRequest<{ narratives: unknown[] }>(`/intelligence/narratives/${q}`);
}

/** Phase 10 legacy national AI snapshot (route preserved). */
export async function fetchNationalIntelligence() {
  return apiRequest<Record<string, unknown>>("/intelligence/national/");
}

const BRIEFING_CACHE_KEY = "nptte_executive_briefing_v1";
const BRIEFING_TTL_MS = 90_000;

export async function fetchExecutiveBriefing() {
  if (typeof window !== "undefined") {
    try {
      const raw = sessionStorage.getItem(BRIEFING_CACHE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as { at: number; data: Record<string, unknown> };
        if (Date.now() - parsed.at < BRIEFING_TTL_MS) {
          return { success: true as const, data: parsed.data };
        }
      }
    } catch {
      /* ignore cache parse */
    }
  }
  const res = await apiRequest<Record<string, unknown>>("/intelligence/executive-briefing/");
  if (res.success && res.data && typeof window !== "undefined") {
    try {
      sessionStorage.setItem(BRIEFING_CACHE_KEY, JSON.stringify({ at: Date.now(), data: res.data }));
    } catch {
      /* quota */
    }
  }
  return res;
}

export async function fetchEnforcementCases() {
  return apiRequest<{ cases: unknown[] }>("/enforcement/cases/");
}

export async function fetchEnforcementRecommendations() {
  return apiRequest<{ recommendations: unknown[] }>("/enforcement/recommendations/");
}

export async function acceptRecommendation(id: string) {
  return apiRequest(`/enforcement/recommendations/${id}/accept/`, { method: "POST", body: "{}" });
}

export async function fetchEnforcementTimeline(caseId?: string) {
  const q = caseId ? `?case_id=${caseId}` : "";
  return apiRequest<{ timeline: unknown[] }>(`/enforcement/timeline/${q}`);
}
