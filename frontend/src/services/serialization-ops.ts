import { apiRequest } from "./api-client";

export type SerializationDashboard = {
  total_serials: number;
  serials_with_scans: number;
  suspicious_scan_events: number;
  packaging_units: number;
  duplicate_scans_24h: number;
};

export async function fetchSerializationDashboard() {
  return apiRequest<SerializationDashboard>("/serialization/dashboard/");
}

export async function fetchSerializationScanHistory(serial?: string) {
  const q = serial ? `?serial_number=${encodeURIComponent(serial)}` : "";
  return apiRequest<{ scans: unknown[]; count: number }>(`/serialization/scan-history/${q}`);
}

export async function decodeSerializationScan(raw_scan: string) {
  return apiRequest<Record<string, string>>("/serialization/decode/", {
    method: "POST",
    body: JSON.stringify({ raw_scan }),
  });
}
