import { apiRequest } from "@/services/api-client";

export type EvidencePhoto = {
  id: string;
  mime: string;
  base64: string;
  upload_status: "pending" | "synced" | "failed";
};

export async function uploadFieldEvidence(payload: {
  device_id: string;
  evidence_type: string;
  notes?: string;
  serial_number?: string;
  case_id?: string;
  latitude?: number;
  longitude?: number;
  photos: EvidencePhoto[];
}) {
  return apiRequest<{ id: string; sync_status: string }>("/mobile/evidence/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function syncEvidenceQueue(device_id: string) {
  return apiRequest<{ synced: number }>("/mobile/evidence/sync/", {
    method: "POST",
    body: JSON.stringify({ device_id }),
  });
}

export async function fetchEvidenceList() {
  return apiRequest<{ evidence: Record<string, unknown>[] }>("/mobile/evidence/");
}
