export type ActivityDetail = {
  id: string;
  activityType: string;
  officerName: string;
  organisationName: string;
  addressLine: string;
  city: string;
  state: string;
  timestamp: string;
  linkedScanId: string;
  linkedEvidenceId: string;
  linkedTaskId: string;
  linkedCaseId: string;
  outcomeStatus: string;
  syncStatus: string;
  deviceId: string;
  auditNote: string;
};

function str(v: unknown): string {
  return v != null && String(v).trim() ? String(v).trim() : "";
}

export function enrichActivityDetail(raw: Record<string, unknown>): ActivityDetail {
  const payload = (raw.payload as Record<string, unknown> | undefined) ?? {};
  const line1 = str(raw.address) || str(payload.address);
  const city = str(raw.city) || str(payload.city);
  const state = str(raw.state) || str(payload.state);
  const addressLine =
    [line1, city, state].filter(Boolean).join(", ") ||
    "Address unavailable in demo data — see payload metadata on web enforcement record.";

  return {
    id: str(raw.id) || "unknown",
    activityType: str(raw.action_type) || str(raw.activity_type) || "operational",
    officerName: str(raw.officer_name) || str(payload.officer) || str(payload.actor) || "Field officer",
    organisationName: str(raw.organisation_name) || str(payload.organisation_name) || "—",
    addressLine,
    city: city || "—",
    state: state || "—",
    timestamp: str(raw.created_at) || new Date().toISOString(),
    linkedScanId: str(raw.linked_scan_id) || str(payload.serial) || str(payload.scan_id),
    linkedEvidenceId: str(raw.linked_evidence_id) || str(payload.evidence_id),
    linkedTaskId: str(raw.linked_task_id) || str(payload.task_id),
    linkedCaseId: str(raw.linked_case_id) || str(payload.case_id),
    outcomeStatus: str(raw.outcome_status) || str(payload.action_status) || str(payload.status) || "recorded",
    syncStatus: str(raw.sync_status) || "synced",
    deviceId: str(raw.device_id) || "—",
    auditNote: str(raw.audit_note) || str(payload.note) || str(payload.signature_note),
  };
}
