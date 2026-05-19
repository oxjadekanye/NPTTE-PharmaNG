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
    }
)

# Aggregates that expose national-level intelligence — regulators only.
REGULATOR_ONLY_AGGREGATES = frozenset(
    {
        "national-risk-current",
        "high-risk-current",
        "open-alerts-current",
        "fraud-flags-current",
        "counterfeit-detections-current",
        "active-investigations-current",
        "products-tracked-current",
        "recalls-current",
    }
)
