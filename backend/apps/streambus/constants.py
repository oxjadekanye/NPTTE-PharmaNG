"""Typed operational event identifiers."""

# Event types
EVT_SCAN = "scan.completed"
EVT_SCAN_SUSPICIOUS = "scan.suspicious"
EVT_ONBOARDING = "onboarding.updated"
EVT_RECALL = "recall.propagated"
EVT_APPROVAL = "approval.recorded"
EVT_INSPECTION = "inspection.recorded"
EVT_NOTIFICATION = "notification.delivered"
EVT_ORGANISATION = "organisation.action"
EVT_TASK = "task.updated"
EVT_TELEMETRY = "telemetry.tick"
EVT_ENFORCEMENT_NOTE = "enforcement.investigation.note"
EVT_ENFORCEMENT_COMMENT = "enforcement.investigation.comment"
EVT_ESCALATION = "escalation.propagated"
EVT_REGIONAL = "regional.alert"

# Severities
SEV_INFO = "INFO"
SEV_WARNING = "WARNING"
SEV_CRITICAL = "CRITICAL"

# Lifecycle states
STATE_PUBLISHED = "published"
STATE_DELIVERED = "delivered"
STATE_REPLAYED = "replayed"
STATE_ACKNOWLEDGED = "acknowledged"
STATE_FAILED = "failed"
STATE_RETRY = "retry"

# Channels
CHANNEL_DB = "database"
CHANNEL_REDIS = "redis"
CHANNEL_SSE = "sse"
CHANNEL_WEBSOCKET = "websocket"

# Phase 20C scoped delivery channels
CH_NATIONAL = "national"
CH_REGIONAL = "regional"
CH_INVESTIGATION = "investigation"
CH_ESCALATION = "escalation"
CH_OFFICER_TASKS = "officer_tasks"
CH_EXECUTIVE = "executive"
