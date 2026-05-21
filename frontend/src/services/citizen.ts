import { apiRequest } from "./api-client";

export async function publicVerify(payload: {
  serial_number?: string;
  qr_token?: string;
  barcode?: string;
}) {
  return apiRequest<Record<string, unknown>>("/public/verify/", {
    method: "POST",
    body: JSON.stringify(payload),
    auth: false,
  });
}

export async function reportCounterfeit(payload: {
  description: string;
  serial_number?: string;
  pharmacy_name?: string;
  state?: string;
}) {
  return apiRequest("/public/report-counterfeit/", {
    method: "POST",
    body: JSON.stringify(payload),
    auth: false,
  });
}

export async function fetchPublicRecalls() {
  return apiRequest<{ recalls: unknown[] }>("/public/recalls/", { auth: false });
}

export async function fetchTrustedPharmacies(state?: string) {
  const q = state ? `?state=${encodeURIComponent(state)}` : "";
  return apiRequest<{ pharmacies: unknown[] }>(`/public/trusted-pharmacies/${q}`, {
    auth: false,
  });
}

export async function fetchVerificationHistory(deviceId?: string) {
  const q = deviceId ? `?device_id=${encodeURIComponent(deviceId)}` : "";
  return apiRequest<{ history: unknown[] }>(`/public/verification-history/${q}`, { auth: false });
}

export async function searchMedication(query: string, state?: string) {
  const q = new URLSearchParams({ q: query });
  if (state) q.set("state", state);
  return apiRequest<Record<string, unknown>>(`/public/medication-search/?${q}`, { auth: false });
}

export async function fetchSafetyGuidance(product?: string, outcome?: string) {
  const q = new URLSearchParams();
  if (product) q.set("product", product);
  if (outcome) q.set("outcome", outcome);
  return apiRequest<Record<string, unknown>>(`/public/safety-guidance/?${q}`, { auth: false });
}

export async function fetchPublicNotices() {
  return apiRequest<{ notices: unknown[] }>("/public/public-notices/", { auth: false });
}
