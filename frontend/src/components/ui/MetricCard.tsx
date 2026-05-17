import clsx from "clsx";
import type { MetricCard as MetricCardType } from "@/shared/types";

const severityStyles = {
  normal: "border-sovereign-700/50",
  warning: "border-amber-500/40 bg-amber-500/5",
  critical: "border-red-500/50 bg-red-500/10",
};

export function MetricCard({ label, value, severity = "normal" }: MetricCardType) {
  return (
    <div
      className={clsx(
        "rounded-xl border bg-sovereign-900/80 p-5 backdrop-blur-sm transition hover:border-sovereign-accent/40",
        severityStyles[severity]
      )}
    >
      <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{label}</p>
      <p className="mt-2 font-mono text-2xl font-semibold text-white">{value}</p>
    </div>
  );
}
