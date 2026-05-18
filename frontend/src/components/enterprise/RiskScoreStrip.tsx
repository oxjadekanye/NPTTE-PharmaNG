"use client";

import clsx from "clsx";
import type { AiRiskScore } from "@/intelligence/ai-risk-simulation";

const bandClass: Record<AiRiskScore["band"], string> = {
  low: "border-emerald-500/30 bg-emerald-500/5 text-emerald-200",
  elevated: "border-amber-500/35 bg-amber-500/10 text-amber-100",
  high: "border-orange-500/40 bg-orange-500/10 text-orange-100",
  critical: "border-rose-500/50 bg-rose-500/15 text-rose-100",
};

export function RiskScoreStrip({ scores }: { scores: AiRiskScore[] }) {
  return (
    <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-5">
      {scores.map((s) => (
        <div
          key={s.domain}
          className={clsx(
            "rounded-xl border px-3 py-3 shadow-inner backdrop-blur-sm transition hover:border-sovereign-accent/40",
            bandClass[s.band]
          )}
        >
          <p className="text-[10px] uppercase tracking-wider opacity-80">{s.label}</p>
          <p className="mt-1 text-2xl font-semibold tabular-nums">{s.score}</p>
          <p className="mt-1 line-clamp-2 text-[10px] opacity-70">{s.rationale}</p>
        </div>
      ))}
    </div>
  );
}
