"use client";

import { AnimatedMetricCard } from "@/components/ui/AnimatedMetricCard";
import type { MetricCard } from "@/shared/types";

export function OverviewGrid({ metrics, animate = true }: { metrics: MetricCard[]; animate?: boolean }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3 2xl:grid-cols-4">
      {metrics.map((m, i) =>
        animate && m.numericValue !== undefined ? (
          <AnimatedMetricCard key={m.label} {...m} pulse={i < 3} />
        ) : (
          <AnimatedMetricCard
            key={m.label}
            {...m}
            numericValue={
              typeof m.value === "number"
                ? m.value
                : Number.isFinite(Number(String(m.value).replace(/[^0-9.]/g, "")))
                  ? Number(String(m.value).replace(/[^0-9.]/g, ""))
                  : undefined
            }
            pulse={i < 3}
          />
        )
      )}
    </div>
  );
}
