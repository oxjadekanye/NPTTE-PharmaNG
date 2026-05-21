export function parseCopilotText(data: Record<string, unknown> | undefined): string | null {
  if (!data) return null;
  const summary = data.summary;
  const reasoning = data.reasoning;
  const parts: string[] = [];
  if (typeof summary === "string" && summary.trim()) parts.push(summary.trim());
  else if (summary && typeof summary === "object") {
    const s = summary as Record<string, unknown>;
    const title = s.title ?? s.body;
    if (typeof title === "string" && title.trim()) parts.push(title.trim());
  }
  if (typeof reasoning === "string" && reasoning.trim()) parts.push(reasoning.trim());
  if (parts.length) return parts.join("\n\n");
  if (typeof data.message === "string" && data.message.trim()) return data.message.trim();
  return null;
}

export type InspectionRecommendationInput = {
  site_passed: boolean;
  product_passed: boolean;
  compliance_passed: boolean;
  failed_items: string[];
  evidence_count: number;
  compliance_score: number;
  inspection_context?: string;
};

export type InspectionRecommendation = {
  risk_rating: string;
  immediate_concerns: string[];
  recommended_enforcement_action: string;
  evidence_required: string[];
  follow_up_timeframe: string;
  escalation_required: boolean;
  source: "api" | "fallback";
};

export function parseInspectionRecommendation(
  data: Record<string, unknown> | undefined
): InspectionRecommendation | null {
  if (!data) return null;
  const actions = data.recommended_actions;
  const concerns = data.immediate_concerns;
  const evidenceReq = data.evidence_required;
  const risk = data.risk_rating ?? data.urgency ?? data.summary;
  if (!risk && !actions) return null;
  return {
    risk_rating: String(risk ?? "medium"),
    immediate_concerns: Array.isArray(concerns)
      ? concerns.map(String)
      : typeof data.reasoning === "string"
        ? [data.reasoning]
        : [],
    recommended_enforcement_action: Array.isArray(actions)
      ? actions.join("; ")
      : String(data.summary ?? data.reasoning ?? ""),
    evidence_required: Array.isArray(evidenceReq) ? evidenceReq.map(String) : [],
    follow_up_timeframe: String(data.follow_up_timeframe ?? "Within 7 days"),
    escalation_required: Boolean(data.escalation_required ?? data.urgency === "critical"),
    source: "api",
  };
}

export function inspectionRecommendationFallback(
  input: InspectionRecommendationInput
): InspectionRecommendation {
  const { compliance_score: score, failed_items: failed, evidence_count: evidenceCount } = input;
  const concerns: string[] = [];
  const evidenceRequired: string[] = [];
  let action =
    "Document findings and update the national enforcement record with officer signature.";
  let timeframe = "Routine follow-up within 14 days";
  let escalation = false;
  let risk = "low";

  const failedLower = failed.map((f) => f.toLowerCase());

  if (score < 40) {
    risk = "critical";
    escalation = true;
    timeframe = "Immediate — within 24 hours";
    concerns.push("Compliance score below 40% — statutory intervention threshold.");
    action =
      "Suspend dispensing of flagged stock, initiate formal enforcement case, and notify regional coordinator.";
  } else if (score < 70) {
    risk = "high";
    timeframe = "Within 72 hours";
    concerns.push("Material gaps in guided inspection checklist.");
  }

  if (!input.product_passed || failedLower.some((f) => f.includes("product"))) {
    concerns.push("Product verification incomplete — serial/batch integrity unconfirmed.");
    action =
      "Quarantine affected lots, re-scan serial samples, and verify batch records against NAFDAC registry.";
    evidenceRequired.push("Photographic evidence of quarantined stock", "Serial scan export");
  }

  if (!input.compliance_passed || failedLower.some((f) => f.includes("compliance"))) {
    concerns.push("Compliance documentation gaps detected.");
    action =
      "Issue corrective action notice, require cold-chain and custody logs, and schedule mandatory re-inspection.";
    timeframe = "Corrective action due within 7 days";
  }

  if (failedLower.some((f) => f.includes("cold-chain") || f.includes("storage"))) {
    concerns.push("Cold-chain or storage conditions failed — temperature excursion risk.");
    action = "Urgent storage inspection — verify refrigeration logs and segregate compromised stock.";
    escalation = true;
    risk = "critical";
    timeframe = "Within 12 hours";
  }

  if (evidenceCount < 1) {
    concerns.push("No photographic evidence captured for this inspection.");
    evidenceRequired.push("Site photos", "Storage area photos", "Sample serial capture");
    action = `${action} Request photographic evidence before closing inspection.`;
  }

  if (!input.site_passed) {
    concerns.push("Site verification incomplete — registration or staff interview pending.");
  }

  if (!concerns.length) {
    concerns.push("Checklist substantially complete — maintain custody chain documentation.");
    action = "Approve routine operations; schedule spot-check within 30 days.";
  }

  return {
    risk_rating: risk,
    immediate_concerns: concerns,
    recommended_enforcement_action: action,
    evidence_required: evidenceRequired.length
      ? evidenceRequired
      : ["Officer signature on enforcement record"],
    follow_up_timeframe: timeframe,
    escalation_required: escalation,
    source: "fallback",
  };
}

export function formatInspectionRecommendation(rec: InspectionRecommendation): string {
  const lines = [
    `Risk rating: ${rec.risk_rating.toUpperCase()}`,
    rec.immediate_concerns.length
      ? `Immediate concerns:\n• ${rec.immediate_concerns.join("\n• ")}`
      : "",
    `Recommended action: ${rec.recommended_enforcement_action}`,
    rec.evidence_required.length
      ? `Evidence required:\n• ${rec.evidence_required.join("\n• ")}`
      : "",
    `Follow-up: ${rec.follow_up_timeframe}`,
    `Escalation required: ${rec.escalation_required ? "Yes" : "No"}`,
  ];
  return lines.filter(Boolean).join("\n\n");
}

export function checklistFallbackRecommendation(score: number): string {
  if (score >= 80) {
    return (
      "Checklist largely complete. Maintain documented custody chain and batch records. " +
      "Escalate only if serial mismatch recurs on re-scan or cold-chain gaps appear."
    );
  }
  if (score >= 50) {
    return (
      "Partial compliance. Prioritize batch record review, cold-chain logs, and staff interviews. " +
      "Schedule follow-up inspection within 7 days and document corrective actions."
    );
  }
  return (
    "Low compliance score. Immediate field actions: quarantine suspect stock, collect serial samples, " +
    "verify recall acknowledgement, and notify regional enforcement coordinator."
  );
}
