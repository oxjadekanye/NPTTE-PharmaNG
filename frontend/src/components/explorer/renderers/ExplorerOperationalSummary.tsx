"use client";

import { memo } from "react";
import { ExplorerSeverityBadge } from "../ExplorerSeverityBadge";
import { formatTimestamp } from "@/services/explorer-format";

type Props = {
  title?: string;
  summary?: string;
  count?: number;
  status?: string;
  riskScore?: number | string;
  confidence?: number | string;
  topStates?: string[];
  topOrganisations?: string[];
  updatedAt?: string;
};

export const ExplorerOperationalSummary = memo(function ExplorerOperationalSummary({
  title,
  summary,
  count,
  status,
  riskScore,
  confidence,
  topStates = [],
  topOrganisations = [],
  updatedAt,
}: Props) {
  return (
    <section className="rounded-lg border border-sovereign-800 bg-sovereign-900/40 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <h3 className="text-sm font-semibold text-white">{title ?? "Operational summary"}</h3>
        {status ? <ExplorerSeverityBadge severity={status} /> : null}
      </div>
      {summary ? <p className="mt-2 text-sm text-slate-200">{summary}</p> : null}
      <dl className="mt-3 grid grid-cols-2 gap-2 text-[11px] text-slate-400">
        {count != null ? (
          <div>
            <dt className="text-slate-500">Records</dt>
            <dd className="font-medium text-white">{count}</dd>
          </div>
        ) : null}
        {riskScore != null ? (
          <div>
            <dt className="text-slate-500">Risk score</dt>
            <dd className="font-medium text-white">{riskScore}</dd>
          </div>
        ) : null}
        {confidence != null ? (
          <div>
            <dt className="text-slate-500">Confidence</dt>
            <dd className="font-medium text-white">{confidence}</dd>
          </div>
        ) : null}
        {updatedAt ? (
          <div className="col-span-2">
            <dt className="text-slate-500">Updated</dt>
            <dd>{formatTimestamp(updatedAt)}</dd>
          </div>
        ) : null}
      </dl>
      {topStates.length > 0 ? (
        <p className="mt-2 text-[10px] text-slate-500">Top states: {topStates.join(", ")}</p>
      ) : null}
      {topOrganisations.length > 0 ? (
        <p className="mt-1 text-[10px] text-slate-500">
          Top organisations: {topOrganisations.join(", ")}
        </p>
      ) : null}
    </section>
  );
});
