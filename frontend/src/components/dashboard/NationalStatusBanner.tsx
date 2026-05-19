"use client";

import clsx from "clsx";
import { computeNationalStatus, NATIONAL_KPIS } from "@/demo/nigeria-intelligence";
import type { NationalStatus } from "@/demo/types";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

const CONFIG: Record<
  NationalStatus,
  { label: string; headline: string; className: string; dot: string }
> = {
  stable: {
    label: "STABLE",
    headline: "National pharmaceutical supply chain within acceptable risk thresholds",
    className: "border-emerald-500/40 bg-emerald-500/10 text-emerald-100",
    dot: "bg-emerald-500",
  },
  warning: {
    label: "WARNING",
    headline: "Elevated counterfeit, shortage, or investigation activity — coordinated response advised",
    className: "border-amber-500/40 bg-amber-500/10 text-amber-100",
    dot: "bg-amber-500",
  },
  critical: {
    label: "CRITICAL",
    headline: "Multiple national risk indicators exceeded — ministerial and emergency channels on standby",
    className: "border-red-500/50 bg-red-500/15 text-red-100",
    dot: "bg-red-500 animate-pulse",
  },
};

export function NationalStatusBanner({ status }: { status?: NationalStatus }) {
  const resolved = status ?? computeNationalStatus(NATIONAL_KPIS);
  const cfg = CONFIG[resolved];
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);

  return (
    <div
      role="button"
      tabIndex={0}
      aria-label="National status. View national risk explorer."
      onClick={() =>
        openDrawer({
          entityType: "national_risk",
          entityId: "national-risk-current",
          title: "National status",
        })
      }
      onKeyDown={(ev) => {
        if (ev.key === "Enter" || ev.key === " ") {
          ev.preventDefault();
          openDrawer({
            entityType: "national_risk",
            entityId: "national-risk-current",
            title: "National status",
          });
        }
      }}
      className={clsx(
        "mb-6 flex cursor-pointer flex-col gap-2 rounded-xl border px-5 py-4 outline-none transition hover:ring-2 hover:ring-sovereign-accent/30 md:flex-row md:items-center md:justify-between",
        cfg.className
      )}
    >
      <div className="flex items-center gap-3">
        <span className={clsx("h-3 w-3 rounded-full", cfg.dot)} aria-hidden />
        <div>
          <p className="text-xs font-bold uppercase tracking-widest">National status · {cfg.label}</p>
          <p className="mt-0.5 text-sm opacity-90">{cfg.headline}</p>
        </div>
      </div>
      <p className="text-[10px] uppercase tracking-wider text-slate-400/80">
        Computed from simulated threat, shortage, recall &amp; investigation indicators (DEMO)
      </p>
    </div>
  );
}
