export type MetricCard = {
  label: string;
  value?: string | number;
  numericValue?: number;
  decimals?: number;
  suffix?: string;
  pulse?: boolean;
  trend?: "up" | "down" | "neutral";
  severity?: "normal" | "warning" | "critical";
  /** Phase 19 — direct entity drill-down. */
  explorer?: { entityType: string; entityId: string };
  /** Phase 20A — resolve true entity via context-route API. */
  explorerContext?: string;
};

export type IncidentRow = {
  id: string;
  code: string;
  title: string;
  severity: string;
  status: string;
  threat_score: string;
  states?: string[];
};
