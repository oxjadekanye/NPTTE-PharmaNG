"use client";

import { memo } from "react";
import { ExplorerSeverityBadge } from "../ExplorerSeverityBadge";
import { formatTimestamp, recordSearchText, type OperationalRecord } from "@/services/explorer-format";

export const ExplorerRecordsTable = memo(function ExplorerRecordsTable({
  records,
  filter,
  onFilterChange,
}: {
  records: OperationalRecord[];
  filter: string;
  onFilterChange: (v: string) => void;
}) {
  const q = filter.trim().toLowerCase();
  const visible = q
    ? records.filter((row) => recordSearchText(row).includes(q))
    : records;

  return (
    <section>
      <div className="flex items-center justify-between gap-2">
        <h4 className="text-[11px] font-semibold uppercase text-slate-400">Operational records</h4>
        <input
          type="search"
          placeholder="Search…"
          value={filter}
          onChange={(ev) => onFilterChange(ev.target.value)}
          className="w-32 rounded border border-sovereign-700 bg-sovereign-900 px-2 py-0.5 text-[10px] text-white"
        />
      </div>
      <div className="mt-2 max-h-64 overflow-auto rounded border border-sovereign-800">
        <table className="w-full text-left text-[11px]">
          <thead className="sticky top-0 bg-sovereign-900 text-slate-500">
            <tr>
              <th className="px-2 py-1">Record</th>
              <th className="px-2 py-1">Severity</th>
              <th className="px-2 py-1">Organisation</th>
              <th className="px-2 py-1">Location</th>
              <th className="px-2 py-1">Detected</th>
            </tr>
          </thead>
          <tbody>
            {visible.length === 0 && (
              <tr>
                <td colSpan={5} className="px-2 py-4 text-center text-slate-500">
                  No matching operational records
                </td>
              </tr>
            )}
            {visible.slice(0, 50).map((row, i) => (
              <tr
                key={String(row.id ?? i)}
                className="border-t border-sovereign-800/60 hover:bg-sovereign-800/30"
              >
                <td className="px-2 py-1.5 text-slate-200">
                  <p className="font-medium">
                    {String(row.title ?? row.name ?? row.case_reference ?? "Record")}
                  </p>
                  {row.recommended_action ? (
                    <p className="mt-0.5 text-[10px] text-slate-500">
                      {String(row.recommended_action)}
                    </p>
                  ) : null}
                </td>
                <td className="px-2 py-1">
                  {row.severity ? (
                    <ExplorerSeverityBadge severity={String(row.severity)} />
                  ) : (
                    <span className="text-slate-500">{String(row.status ?? "—")}</span>
                  )}
                </td>
                <td className="px-2 py-1 text-slate-400">{String(row.organisation ?? "—")}</td>
                <td className="px-2 py-1 text-slate-500">
                  {[row.city, row.state].filter(Boolean).join(", ") || String(row.address ?? "—")}
                </td>
                <td className="px-2 py-1 text-slate-500">{formatTimestamp(row.detected_at)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
});
