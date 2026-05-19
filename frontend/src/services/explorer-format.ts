/** Human-readable formatting for explorer operational UI (no raw JSON). */
export type OperationalRecord = Record<string, unknown>;

export function humanLabel(key: string): string {
  return key.replace(/_/g, " ").replace(/\b\w/g, (c) => c.toUpperCase());
}

export function formatTimestamp(value: unknown): string {
  if (!value) return "—";
  const d = new Date(String(value));
  if (Number.isNaN(d.getTime())) return String(value);
  return d.toLocaleString(undefined, {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

export function recordSearchText(row: OperationalRecord): string {
  const parts = [
    row.title,
    row.organisation,
    row.product,
    row.state,
    row.city,
    row.status,
    row.severity,
    row.serial,
    row.batch,
    row.assigned_officer,
  ];
  return parts.filter(Boolean).join(" ").toLowerCase();
}

export function recordEntityKind(row: OperationalRecord): string {
  return String(row.entity_type ?? "record");
}
