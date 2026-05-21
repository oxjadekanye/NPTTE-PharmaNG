export type AlertDetail = {
  id: string;
  title: string;
  severity: string;
  priority: string;
  organisationName: string;
  addressLine: string;
  city: string;
  lga: string;
  state: string;
  detectedAt: string;
  productName: string;
  batch: string;
  serial: string;
  riskExplanation: string;
  recommendedAction: string;
  linkedTaskId: string;
  linkedInvestigationId: string;
  alertType: string;
};

function str(v: unknown): string {
  return v != null && String(v).trim() ? String(v).trim() : "";
}

function formatAddress(parts: string[]): string {
  const joined = parts.filter(Boolean).join(", ");
  return joined || "";
}

/** Enrich alert list/feed rows into operational detail cards (demo-safe). */
export function enrichAlertDetail(raw: Record<string, unknown>): AlertDetail {
  const evidence =
    (raw.evidence_payload as Record<string, unknown> | undefined) ??
    (raw.payload as Record<string, unknown> | undefined) ??
    {};

  const orgName = str(raw.organisation_name) || str(evidence.organisation_name) || "Organisation not listed";
  const city = str(raw.city) || str(evidence.city);
  const lga = str(raw.lga) || str(evidence.lga) || (city ? `${city} LGA` : "");
  const state = str(raw.state) || str(evidence.state);
  const line1 = str(raw.address_line) || str(evidence.address) || str(raw.address);
  const line2 = str(raw.address_line_2);
  const addressLine =
    formatAddress([line1, line2, city, state]) ||
    (state ? `${state} — full street address unavailable in demo data` : "Address unavailable in demo data");

  return {
    id: str(raw.id) || "unknown",
    title: str(raw.title) || "National alert",
    severity: str(raw.severity) || str(raw.priority) || "INFO",
    priority: str(raw.priority) || str(raw.risk_level) || str(raw.severity) || "INFO",
    organisationName: orgName,
    addressLine,
    city: city || "—",
    lga: lga || "—",
    state: state || "—",
    detectedAt:
      str(raw.detected_at) || str(evidence.detected_at) || str(raw.created_at) || new Date().toISOString(),
    productName: str(raw.product_name) || str(evidence.product),
    batch: str(raw.batch) || str(evidence.batch),
    serial: str(raw.serial) || str(evidence.serial),
    riskExplanation:
      str(raw.risk_explanation) ||
      str(raw.description) ||
      str(raw.summary) ||
      "Operational risk flagged by national monitoring systems.",
    recommendedAction:
      str(raw.recommended_action) ||
      str(evidence.recommended_action) ||
      "Assign field verification and document findings in the enforcement record.",
    linkedTaskId: str(raw.linked_task_id) || str(evidence.task_id),
    linkedInvestigationId: str(raw.linked_investigation_id) || str(evidence.investigation_id),
    alertType: str(raw.alert_type) || str(raw.kind) || "national_alert",
  };
}
