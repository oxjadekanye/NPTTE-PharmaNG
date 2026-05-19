"use client";

import clsx from "clsx";
import { useAnimatedCounter, formatMetricValue } from "@/hooks/useAnimatedCounter";
import { openExplorerTarget } from "@/lib/explorer-routing";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";
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
  explorer,
  explorerContext,
}: MetricCard & { numericValue?: number; decimals?: number; pulse?: boolean; suffix?: string }) {
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);
  const target = numericValue ?? (typeof value === "number" ? value : parseFloat(String(value).replace(/,/g, "")));
  const canAnimate = Number.isFinite(target) && !Number.isNaN(target);
  const animated = useAnimatedCounter(canAnimate ? target : 0, 1100, canAnimate);
  const display = canAnimate
    ? `${formatMetricValue(animated, decimals)}${suffix}`
    : String(value ?? "—");

  const interactive = Boolean(explorer || explorerContext);
  const activate = () => {
    void openExplorerTarget(openDrawer, { title: label, explorer, context: explorerContext });
  };

  return (
    <div
      role={interactive ? "button" : undefined}
      tabIndex={interactive ? 0 : undefined}
      aria-label={interactive ? `${label}. View operational details.` : undefined}
      onClick={interactive ? activate : undefined}
      onKeyDown={
        interactive
          ? (ev) => {
              if (ev.key === "Enter" || ev.key === " ") {
                ev.preventDefault();
                activate();
              }
            }
          : undefined
      }
      className={clsx(
        "group relative overflow-hidden rounded-xl border bg-sovereign-900/80 p-5 shadow-lg shadow-black/20 backdrop-blur-sm transition duration-300 hover:-translate-y-0.5 hover:border-sovereign-accent/50 hover:shadow-sovereign-accent/10",
        severityStyles[severity],
        interactive && "cursor-pointer focus:outline-none focus:ring-2 focus:ring-sovereign-accent/40"
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
      {interactive && (
        <p className="mt-2 text-[10px] text-sovereign-accent/80 opacity-0 transition group-hover:opacity-100">
          View details · Enter
        </p>
      )}
    </div>
  );
}
