import type { ExplorerOpenPayload } from "@/store/explorer-drawer-store";
import { isAggregateEntityId } from "./explorer-format";

/** Reverse map aggregate pseudo-ID → dashboard context key for full-page routing. */
const AGGREGATE_TO_CONTEXT: Record<string, string> = {
  "live-national-threat-composite": "national_status",
  "national-risk-current": "national_risk",
  "national-verifications-current": "verifications_24h",
  "open-alerts-current": "open_alerts",
  "fraud-flags-current": "fraud_flags",
  "counterfeit-detections-current": "counterfeit_detections",
  "active-investigations-current": "active_investigations",
  "products-tracked-current": "products_tracked",
  "recalls-current": "recalls",
  "emergency-recalls-current": "emergency_recalls",
  "blacklisted-batches-current": "blacklisted_batches",
  "api-health-current": "api_health",
  "medicine-stability-current": "medicine_stability",
  "counterfeit-risk-forecast-current": "counterfeit_risk_forecast",
  "shortage-pressure-current": "shortage_pressure",
  "import-disruption-current": "import_disruption",
  "enforcement-readiness-current": "enforcement_readiness",
  "compliance-rate-current": "compliance_rate",
  "scan-success-rate-current": "scan_success_rate",
  "counterfeit-reduction-current": "counterfeit_reduction",
  "public-health-risk-current": "public_health_risk",
  "urgent-actions-current": "urgent_actions",
  "national-ai-intelligence-current": "national_ai_intelligence",
  "command-activity-current": "command_activity",
  "shortage-alerts-current": "shortage_alerts",
};

export function contextKeyForAggregateId(aggregateId: string): string | null {
  return AGGREGATE_TO_CONTEXT[aggregateId] ?? null;
}

/** Stable full-page URL — context routes for aggregates, entity routes for real records. */
export function explorerFullPageHref(target: ExplorerOpenPayload): string {
  if (target.contextKey) {
    return `/regulator/explorer/context/${encodeURIComponent(target.contextKey)}`;
  }
  const ctx = contextKeyForAggregateId(target.entityId);
  if (ctx) {
    return `/regulator/explorer/context/${encodeURIComponent(ctx)}`;
  }
  if (isAggregateEntityId(target.entityId)) {
    return `/regulator/explorer/aggregate/${encodeURIComponent(target.entityId)}`;
  }
  return `/regulator/explorer/${encodeURIComponent(target.entityType)}/${encodeURIComponent(target.entityId)}`;
}
