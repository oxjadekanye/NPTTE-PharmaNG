"use client";

import { memo } from "react";

export const ExplorerRiskFactors = memo(function ExplorerRiskFactors({
  risk,
}: {
  risk: Record<string, unknown> | null;
}) {
  if (!risk || Object.keys(risk).length === 0) {
    return (
      <p className="text-[11px] text-slate-500">No risk breakdown available for this context.</p>
    );
  }
  const reasons = (risk.reasons as string[]) ?? [];
  const score = risk.score ?? risk.risk_score;
  return (
    <section className="rounded border border-sovereign-800 p-2">
      <h4 className="text-[11px] font-semibold uppercase text-slate-400">Risk factors</h4>
      {score != null && (
        <p className="mt-1 text-sm font-medium text-white">Score: {String(score)}</p>
      )}
      {reasons.length > 0 ? (
        <ul className="mt-2 list-disc space-y-1 pl-4 text-[11px] text-slate-300">
          {reasons.slice(0, 8).map((r, i) => (
            <li key={i}>{r}</li>
          ))}
        </ul>
      ) : (
        <p className="mt-1 text-[11px] text-slate-400">{String(risk.status ?? risk.summary ?? "")}</p>
      )}
    </section>
  );
});
