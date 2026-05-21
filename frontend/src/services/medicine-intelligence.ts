import { apiRequest } from "./api-client";

export async function fetchMedicineIntelligence(q?: string) {
  const suffix = q ? `?q=${encodeURIComponent(q)}` : "";
  return apiRequest<{ medicines: unknown[]; count: number }>(`/intelligence/medicines/${suffix}`);
}

export async function fetchMedicineDetail(id: string) {
  return apiRequest<Record<string, unknown>>(`/intelligence/medicines/${id}/`);
}

export async function fetchManufacturerIntelligence() {
  return apiRequest<{ manufacturers: unknown[] }>("/intelligence/manufacturers/");
}

export async function fetchShortageRisk() {
  return apiRequest<Record<string, unknown>>("/intelligence/shortage-risk/");
}

export async function fetchCounterfeitRisk() {
  return apiRequest<{ summary: unknown; analysis: unknown }>("/intelligence/counterfeit-risk/");
}
