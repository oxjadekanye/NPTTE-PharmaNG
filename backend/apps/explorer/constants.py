"""Supported explorer entity types and aggregate pseudo-IDs."""

ENTITY_TYPES = frozenset(
    {
        "national_risk",
        "regional_risk",
        "product_risk",
        "organisation_risk",
        "intelligence_signal",
        "counterfeit_cluster",
        "enforcement_case",
        "enforcement_recommendation",
        "recall",
        "batch",
        "serial",
        "scan_event",
        "product",
        "organisation",
        "pharmacy",
        "manufacturer",
        "distributor",
        "warehouse",
        "customs_event",
        "alert",
        "notification",
        "incident",
        "task",
        "document",
        "timeline_entry",
    }
)

AGGREGATE_IDS = frozenset(
    {
        "national-risk-current",
        "high-risk-current",
        "open-alerts-current",
        "fraud-flags-current",
        "counterfeit-detections-current",
        "active-investigations-current",
        "products-tracked-current",
        "recalls-current",
        "command-activity-current",
        # Phase 20A.2 — executive & command context aggregates
        "live-national-threat-composite",
        "api-health-current",
        "national-ai-intelligence-current",
        "medicine-stability-current",
        "counterfeit-risk-forecast-current",
        "shortage-pressure-current",
        "import-disruption-current",
        "enforcement-readiness-current",
        "national-verifications-current",
        "compliance-rate-current",
        "scan-success-rate-current",
        "counterfeit-reduction-current",
        "public-health-risk-current",
        "urgent-actions-current",
        "emergency-recalls-current",
        "blacklisted-batches-current",
        "cold-chain-breaches-current",
        "customs-holds-current",
        "invalid-serials-current",
        "duplicate-serials-current",
        "recall-non-acknowledgements-current",
        "shortage-alerts-current",
        "public-reports-current",
    }
)

# Aggregates that expose national-level intelligence — regulators only.
REGULATOR_ONLY_AGGREGATES = AGGREGATE_IDS - frozenset({"command-activity-current"})
