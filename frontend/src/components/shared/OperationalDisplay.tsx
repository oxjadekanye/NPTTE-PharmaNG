"use client";

import { humanLabel, formatTimestamp } from "@/services/explorer-format";

/** Key-value panel for API objects — no raw JSON. */
export function OperationalKeyValuePanel({
  data,
  title,
  emptyMessage = "No data available.",
}: {
  data: Record<string, unknown> | null | undefined;
  title?: string;
  emptyMessage?: string;
}) {
  if (!data || Object.keys(data).length === 0) {
    return <p className="text-xs text-slate-500">{emptyMessage}</p>;
  }
  const entries = Object.entries(data).filter(([, v]) => v !== null && v !== undefined && v !== "");
  return (
    <div className="rounded-lg border border-sovereign-800 bg-sovereign-950/60 p-3">
      {title ? <p className="mb-2 text-[11px] font-semibold uppercase text-slate-400">{title}</p> : null}
      <dl className="grid gap-1 text-[11px]">
        {entries.slice(0, 24).map(([k, v]) => (
          <div key={k} className="flex justify-between gap-2 border-b border-sovereign-800/50 py-1">
            <dt className="text-slate-500">{humanLabel(k)}</dt>
            <dd className="max-w-[60%] truncate text-right text-slate-200">{formatValue(v)}</dd>
          </div>
        ))}
      </dl>
    </div>
  );
}

export function OperationalListPanel({
  items,
  title,
  renderItem,
  emptyMessage = "No records.",
}: {
  items: unknown[];
  title?: string;
  renderItem?: (item: Record<string, unknown>, index: number) => React.ReactNode;
  emptyMessage?: string;
}) {
  if (!items?.length) return <p className="text-xs text-slate-500">{emptyMessage}</p>;
  return (
    <div className="rounded-lg border border-sovereign-800 bg-sovereign-950/60 p-3">
      {title ? <p className="mb-2 text-[11px] font-semibold uppercase text-slate-400">{title}</p> : null}
      <ul className="max-h-64 space-y-2 overflow-auto text-[11px]">
        {items.map((raw, i) => {
          const row = (raw && typeof raw === "object" ? raw : { value: raw }) as Record<string, unknown>;
          return (
            <li key={String(row.id ?? i)} className="rounded border border-sovereign-800/80 px-2 py-1.5">
              {renderItem ? renderItem(row, i) : <DefaultRow row={row} />}
            </li>
          );
        })}
      </ul>
    </div>
  );
}

function DefaultRow({ row }: { row: Record<string, unknown> }) {
  return (
    <>
      <p className="font-medium text-slate-200">{String(row.title ?? row.name ?? row.label ?? row.id ?? "Item")}</p>
      {row.status ? <p className="text-slate-500">Status: {String(row.status)}</p> : null}
      {row.severity ? <p className="text-slate-500">Severity: {String(row.severity)}</p> : null}
    </>
  );
}

function formatValue(v: unknown): string {
  if (v === null || v === undefined) return "—";
  if (typeof v === "boolean") return v ? "Yes" : "No";
  if (typeof v === "number") return String(v);
  if (typeof v === "string") {
    if (/^\d{4}-\d{2}-\d{2}/.test(v)) return formatTimestamp(v);
    return v;
  }
  if (Array.isArray(v)) return v.length ? `${v.length} items` : "—";
  if (typeof v === "object") return `${Object.keys(v as object).length} fields`;
  return String(v);
}
