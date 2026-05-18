import { API_BASE, ApiError, apiRequest } from "./api-client";

function authHeaders(): Headers {
  const h = new Headers();
  h.set("Content-Type", "application/json");
  if (typeof window !== "undefined") {
    const token = localStorage.getItem("nptte_access_token");
    if (token) h.set("Authorization", `Bearer ${token}`);
  }
  return h;
}

async function drfList(path: string): Promise<unknown[]> {
  const res = await fetch(`${API_BASE}${path}`, { headers: authHeaders() });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new ApiError((json as { message?: string })?.message ?? res.statusText, res.status, json);
  }
  const j = json as { results?: unknown[] };
  return Array.isArray(json) ? json : j.results ?? [];
}

export async function fetchPendingBatches() {
  return drfList("/regulatory/batches/pending/");
}

export async function approveBatch(batchId: string, notes?: string) {
  return apiRequest(`/regulatory/batches/${batchId}/approve/`, {
    method: "POST",
    body: JSON.stringify({ notes: notes ?? "" }),
  });
}

export async function rejectBatch(batchId: string, reason: string) {
  return apiRequest(`/regulatory/batches/${batchId}/reject/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export async function recallBatch(batchId: string, reason: string) {
  return apiRequest(`/regulatory/batches/${batchId}/recall/`, {
    method: "POST",
    body: JSON.stringify({ reason }),
  });
}

export async function fetchBatchAuditTrail(batchId: string) {
  return drfList(`/regulatory/batches/${batchId}/audit-trail/`);
}

export async function regulatorVerifyLookup(serialNumber: string) {
  return apiRequest<Record<string, unknown>>("/regulatory/verification/lookup/", {
    method: "POST",
    body: JSON.stringify({ serial_number: serialNumber }),
  });
}

export async function fetchTraceabilityTransactions(params?: string) {
  const q = params ? `?${params}` : "";
  return drfList(`/traceability/transactions${q}`);
}

export async function fetchRecallAffected(batchId: string) {
  return apiRequest<{ pharmacy_organisation_ids?: string[] }>(
    `/regulatory/batches/recall-affected/?batch_id=${encodeURIComponent(batchId)}`
  );
}
