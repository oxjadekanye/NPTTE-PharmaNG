"use client";

import clsx from "clsx";
import { useAnimatedCounter, formatMetricValue } from "@/hooks/useAnimatedCounter";
import type { MetricCard } from "@/shared/types";

const severityStyles = {
  normal: "border-sovereign-700/50",
  warning: "border-amber-500/40 bg-amber-500/5",
  critical: "border-red-500/50 bg-red-500/10",
};

export function AnimatedMetricCard({
  label,
  value,
  numericValue,
  decimals = 0,
  severity = "normal",
  pulse = false,
  suffix = "",
}: MetricCard & { numericValue?: number; decimals?: number; pulse?: boolean; suffix?: string }) {
  const target = numericValue ?? (typeof value === "number" ? value : parseFloat(String(value).replace(/,/g, "")));
  const canAnimate = Number.isFinite(target) && !Number.isNaN(target);
  const animated = useAnimatedCounter(canAnimate ? target : 0, 1100, canAnimate);
  const display = canAnimate
    ? `${formatMetricValue(animated, decimals)}${suffix}`
    : String(value ?? "—");

  return (
    <div
      className={clsx(
        "group relative overflow-hidden rounded-xl border bg-sovereign-900/80 p-5 shadow-lg shadow-black/20 backdrop-blur-sm transition duration-300 hover:-translate-y-0.5 hover:border-sovereign-accent/50 hover:shadow-sovereign-accent/10",
        severityStyles[severity]
      )}
    >
      {pulse && (
        <span className="absolute right-4 top-4 flex h-2 w-2">
          <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-emerald-400 opacity-60" />
          <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-500" />
        </span>
      )}
      <p className="text-xs font-medium uppercase tracking-wider text-slate-400">{label}</p>
      <p className="mt-2 font-mono text-2xl font-semibold tabular-nums text-white transition-all group-hover:text-sovereign-accent">
        {display}
      </p>
    </div>
  );
}
