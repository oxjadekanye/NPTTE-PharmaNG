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

/** Full site line: org name, type, street address, city, state. */
export function formatLocation(row: OperationalRecord): string {
  const org = row.organisation ? String(row.organisation) : "";
  const orgType = row.organisation_type ? humanLabel(String(row.organisation_type)) : "";
  const full = row.full_address ? String(row.full_address) : "";
  const street = [row.address, row.address_line_2].filter(Boolean).join(", ");
  const locality = [row.city, row.state].filter(Boolean).join(", ");
  const parts = [
    org && orgType ? `${org} (${orgType})` : org || orgType,
    full || street,
    locality,
  ].filter((p) => p && p.length > 0);
  return parts.join(" · ") || "—";
}

/** Extract record rows from API payloads (array or paginated slice). */
export function normalizeExplorerRecords(source: unknown): OperationalRecord[] {
  if (!source) return [];
  if (Array.isArray(source)) {
    return source.filter((r) => r && typeof r === "object") as OperationalRecord[];
  }
  if (typeof source === "object") {
    const block = source as { items?: unknown[]; records?: unknown };
    if (Array.isArray(block.items)) {
      return block.items.filter((r) => r && typeof r === "object") as OperationalRecord[];
    }
    if (block.records) return normalizeExplorerRecords(block.records);
  }
  return [];
}

export function recordSearchText(row: OperationalRecord): string {
  const parts = [
    row.title,
    row.organisation,
    row.organisation_type,
    row.full_address,
    row.address,
    row.address_line_2,
    row.city,
    row.state,
    row.product,
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

export function isAggregateEntityId(entityId: string): boolean {
  return Boolean(entityId && (entityId.endsWith("-current") || entityId.includes("-composite")));
}
