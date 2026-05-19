"use client";

import { memo } from "react";
import { formatTimestamp, humanLabel } from "@/services/explorer-format";

export const ExplorerEvidencePanel = memo(function ExplorerEvidencePanel({
  items,
}: {
  items: Record<string, unknown>[];
}) {
  if (!items.length) {
    return <p className="text-[11px] text-slate-500">No evidence items on file.</p>;
  }
  return (
    <ul className="space-y-2">
      {items.slice(0, 10).map((row, i) => (
        <li
          key={String(row.id ?? i)}
          className="rounded border border-sovereign-800 bg-sovereign-900/50 px-2 py-1.5 text-[11px]"
        >
          <p className="font-medium text-slate-200">
            {String(row.title ?? row.type ?? row.kind ?? "Evidence item")}
          </p>
          {row.description ? (
            <p className="mt-0.5 text-slate-400">{String(row.description)}</p>
          ) : null}
          <p className="mt-1 text-[10px] text-slate-500">
            {row.source ? `${humanLabel(String(row.source))} · ` : ""}
            {formatTimestamp(row.captured_at ?? row.created_at ?? row.timestamp)}
          </p>
        </li>
      ))}
    </ul>
  );
});
