import { apiRequest } from "./api-client";

export async function fetchShipmentTimeline(tracking?: string) {
  const q = tracking ? `?tracking_number=${encodeURIComponent(tracking)}` : "";
  return apiRequest<{ shipments: unknown[]; custody_audit: unknown[] }>(
    `/traceability/supply-chain/shipments/${q}`
  );
}

export async function fetchCustodyExplorer() {
  return apiRequest<{ transfers: unknown[]; customs_stages: unknown[] }>(
    "/traceability/supply-chain/custody/"
  );
}

export async function fetchRecallOrchestration() {
  return apiRequest<{ campaigns: unknown[]; active_count: number }>(
    "/traceability/recall-orchestration/"
  );
}
