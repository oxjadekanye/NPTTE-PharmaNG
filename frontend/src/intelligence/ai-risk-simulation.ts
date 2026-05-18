/**
 * Phase 9 — deterministic client-side risk simulation (not ML).
 * Produces enterprise-grade scorecards for dashboards without altering backend models.
 */

export type AiRiskDomain =
  | "counterfeit"
  | "distribution"
  | "pharmacy_fraud"
  | "scan_cluster"
  | "diversion"
  | "shortage"
  | "inventory_motion";

export interface AiRiskScore {
  domain: AiRiskDomain;
  label: string;
  score: number;
  band: "low" | "elevated" | "high" | "critical";
  rationale: string;
}

function bandFor(score: number): AiRiskScore["band"] {
  if (score >= 85) return "critical";
  if (score >= 65) return "high";
  if (score >= 40) return "elevated";
  return "low";
}

function mix(seed: string, salt: number): number {
  let h = 0;
  for (let i = 0; i < seed.length; i += 1) {
    h = (h << 5) - h + seed.charCodeAt(i);
    h |= 0;
  }
  return Math.abs((h + salt * 9973) % 10000) / 10000;
}

export function computePortalRiskScores(portalId: string): AiRiskScore[] {
  const bases: { domain: AiRiskDomain; label: string; salt: number; template: string }[] = [
    { domain: "counterfeit", label: "Counterfeit probability", salt: 1, template: "Serial entropy vs. national baseline" },
    { domain: "distribution", label: "Abnormal distribution", salt: 2, template: "Velocity vs. licensed corridor norms" },
    { domain: "pharmacy_fraud", label: "Pharmacy fraud", salt: 3, template: "Dispense-to-scan ratio anomalies" },
    { domain: "scan_cluster", label: "Unusual scan clustering", salt: 4, template: "Geo-temporal concentration index" },
    { domain: "diversion", label: "Diversion risk", salt: 5, template: "Wholesale bypass pathway signals" },
    { domain: "shortage", label: "Regional shortage forecast", salt: 6, template: "Demand shock + stock depth model (sim)" },
    { domain: "inventory_motion", label: "Suspicious inventory motion", salt: 7, template: "Intra-node transfer friction index" },
  ];
  return bases.map((b) => {
    const raw = 18 + mix(portalId, b.salt) * 72;
    const score = Math.round(raw * 10) / 10;
    return {
      domain: b.domain,
      label: b.label,
      score,
      band: bandFor(score),
      rationale: `${b.template} — portal ${portalId.toUpperCase()} (simulated).`,
    };
  });
}
