export type MetricCard = {
  label: string;
  value?: string | number;
  numericValue?: number;
  decimals?: number;
  suffix?: string;
  pulse?: boolean;
  trend?: "up" | "down" | "neutral";
  severity?: "normal" | "warning" | "critical";
  /** Phase 19 — open intelligence drawer when set (regulator shell). */
  explorer?: { entityType: string; entityId: string };
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
