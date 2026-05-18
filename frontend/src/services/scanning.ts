import { apiRequest } from "./api-client";

export type ScanType =
  | "citizen_verify"
  | "pharmacy_receive"
  | "pharmacy_dispense"
  | "regulator_inspection"
  | "customs_verify"
  | "warehouse_receive";

export type ScanIngestPayload = {
  serial_number: string;
  scan_type: ScanType;
  actor_role: string;
  organisation?: string;
  device_id?: string;
  latitude?: number;
  longitude?: number;
  offline_timestamp?: string;
  sync_status?: "pending" | "synced" | "failed";
  replay_nonce?: string;
};

export type ScanIngestResult = {
  id: string;
  serial_number: string;
  scan_type: string;
  actor_role: string;
  outcome_label: string;
  sync_status: string;
  risk_score: number;
  created_at: string;
  result: Record<string, unknown>;
  alerts: {
    recall_alert: boolean;
    suspicious_scan_alert: boolean;
    counterfeit_warning: boolean;
    failed_sync_warning: boolean;
  };
};

export async function ingestScan(payload: ScanIngestPayload, auth = true) {
  return apiRequest<ScanIngestResult>("/scanning/ingest/", {
    method: "POST",
    body: JSON.stringify(payload),
    auth: payload.scan_type === "citizen_verify" ? false : auth,
  });
}

export async function syncOfflineScans(items: ScanIngestPayload[]) {
  return apiRequest<{ synced: number; results: ScanIngestResult[] }>("/scanning/sync-pending/", {
    method: "POST",
    body: JSON.stringify({ items }),
  });
}

export async function fetchScanHistory(serial?: string) {
  const q = serial ? `?serial_number=${encodeURIComponent(serial)}` : "";
  return apiRequest<{ scans: ScanIngestResult[]; count: number }>(`/scanning/history/${q}`);
}
