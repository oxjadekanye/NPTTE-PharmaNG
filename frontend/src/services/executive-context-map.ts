/**
 * Executive card → unique operational context (never generic national-risk-current).
 */
import { resolveContextTarget, type ContextTarget } from "./explorer-context-map";

const EXECUTIVE_MAP: Record<string, string> = {
  live_national_threat_composite: "live_national_threat_composite",
  "live-national-threat-composite": "live_national_threat_composite",
  api_health: "api_health",
  api_health_current: "api_health",
  national_ai_intelligence: "national_ai_intelligence",
  national_ai: "national_ai_intelligence",
  medicine_stability: "medicine_stability",
  sovereign_briefing: "medicine_stability",
  counterfeit_risk_forecast: "counterfeit_risk_forecast",
  shortage_pressure: "shortage_pressure",
  import_disruption: "import_disruption",
  enforcement_readiness: "enforcement_readiness",
  national_verifications: "national_verifications",
  verifications_24h: "verifications_24h",
  compliance_rate: "compliance_rate",
  scan_success_rate: "scan_success_rate",
  counterfeit_reduction: "counterfeit_reduction",
  public_health_risk: "public_health_risk",
  urgent_actions: "urgent_actions",
};

export function resolveExecutiveContext(contextKey: string, title?: string): ContextTarget {
  const norm = (contextKey || "").trim().toLowerCase().replace(/-/g, "_");
  const mapped = EXECUTIVE_MAP[norm] ?? norm;
  return resolveContextTarget(mapped, title);
}

export const EXECUTIVE_CARD_CONTEXTS = Object.values(EXECUTIVE_MAP);
