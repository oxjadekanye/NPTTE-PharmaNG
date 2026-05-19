import { ExplorerSeverityBadge } from "./ExplorerSeverityBadge";

type Contribution = { factor?: string; contribution?: number; count?: number; description?: string };

export function ExplorerRiskPanel({ risk }: { risk: Record<string, unknown> | null }) {
  if (!risk || Object.keys(risk).length === 0) return null;
  const contributions = (risk.contributions as Contribution[]) ?? [];
  const score = risk.score ?? risk.national_score;
  const status = String(risk.status ?? "");

  return (
    <section className="rounded-lg border border-sovereign-800 bg-sovereign-900/50 p-3">
      <div className="flex flex-wrap items-center gap-2">
        <h4 className="text-[11px] font-semibold uppercase text-slate-400">Risk breakdown</h4>
        {status && <ExplorerSeverityBadge severity={status} />}
        {score != null && <span className="text-xs text-slate-300">Score {String(score)}</span>}
      </div>
      {contributions.length > 0 ? (
        <ul className="mt-3 space-y-2">
          {contributions.map((c, i) => (
            <li key={i} className="flex justify-between gap-2 text-xs text-slate-400">
              <span>{c.factor ?? c.description ?? "Factor"}</span>
              <span className="tabular-nums text-slate-200">{String(c.contribution ?? c.count ?? "—")}</span>
            </li>
          ))}
        </ul>
      ) : (
        <ul className="mt-2 space-y-1 text-xs text-slate-400">
          {((risk.reasons as string[]) ?? []).map((r, i) => (
            <li key={i}>• {r}</li>
          ))}
        </ul>
      )}
    </section>
  );
}
