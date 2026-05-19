/** Client-side context → entity hints for instant drawer open (mirrors backend router). */
export type ContextTarget = { entityType: string; entityId: string; title?: string };

const MAP: Record<string, ContextTarget> = {
  national_status: { entityType: "national_risk", entityId: "live-national-threat-composite", title: "National status" },
  national_risk: { entityType: "national_risk", entityId: "national-risk-current", title: "National risk" },
  verifications_24h: { entityType: "national_risk", entityId: "national-verifications-current", title: "Verifications (24h)" },
  verifications: { entityType: "national_risk", entityId: "national-verifications-current" },
  counterfeit_detections: { entityType: "national_risk", entityId: "counterfeit-detections-current", title: "Counterfeit detections" },
  open_alerts: { entityType: "national_risk", entityId: "open-alerts-current", title: "Open alerts" },
  fraud_flags: { entityType: "national_risk", entityId: "fraud-flags-current", title: "Fraud flags" },
  active_investigations: { entityType: "national_risk", entityId: "active-investigations-current", title: "Active investigations" },
  products_tracked: { entityType: "national_risk", entityId: "products-tracked-current" },
  recalls: { entityType: "national_risk", entityId: "recalls-current" },
  emergency_recalls: { entityType: "national_risk", entityId: "emergency-recalls-current", title: "Emergency recalls" },
  blacklisted_batches: { entityType: "national_risk", entityId: "blacklisted-batches-current" },
  live_national_threat_composite: { entityType: "national_risk", entityId: "live-national-threat-composite" },
  api_health: { entityType: "national_risk", entityId: "api-health-current", title: "API health" },
  medicine_stability: { entityType: "national_risk", entityId: "medicine-stability-current" },
  counterfeit_risk_forecast: { entityType: "national_risk", entityId: "counterfeit-risk-forecast-current" },
  shortage_pressure: { entityType: "national_risk", entityId: "shortage-pressure-current" },
  enforcement_readiness: { entityType: "national_risk", entityId: "enforcement-readiness-current" },
  urgent_actions: { entityType: "national_risk", entityId: "urgent-actions-current" },
  national_ai_intelligence: { entityType: "national_risk", entityId: "national-ai-intelligence-current" },
  command_activity: { entityType: "national_risk", entityId: "command-activity-current" },
  shortage_alerts: { entityType: "national_risk", entityId: "shortage-alerts-current" },
};

export function resolveContextTarget(contextKey: string, fallbackTitle?: string): ContextTarget {
  const key = (contextKey || "").trim().toLowerCase().replace(/-/g, "_");
  const hit = MAP[key];
  if (hit) return { ...hit, title: fallbackTitle ?? hit.title };
  return {
    entityType: "national_risk",
    entityId: "national-risk-current",
    title: fallbackTitle ?? contextKey,
  };
}

export const HOT_PREFETCH_CONTEXTS = [
  "national_status",
  "verifications_24h",
  "counterfeit_detections",
  "open_alerts",
  "fraud_flags",
  "active_investigations",
  "emergency_recalls",
  "blacklisted_batches",
  "live_national_threat_composite",
  "api_health",
  "medicine_stability",
  "counterfeit_risk_forecast",
  "shortage_pressure",
  "enforcement_readiness",
  "urgent_actions",
] as const;
