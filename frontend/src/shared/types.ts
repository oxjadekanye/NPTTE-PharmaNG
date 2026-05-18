export type MetricCard = {
  label: string;
  value?: string | number;
  numericValue?: number;
  decimals?: number;
  suffix?: string;
  pulse?: boolean;
  trend?: "up" | "down" | "neutral";
  severity?: "normal" | "warning" | "critical";
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
