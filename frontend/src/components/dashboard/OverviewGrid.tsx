"use client";

import { MetricCard } from "@/components/ui/MetricCard";
import type { MetricCard as Metric } from "@/shared/types";

export function OverviewGrid({ metrics }: { metrics: Metric[] }) {
  return (
    <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
      {metrics.map((m) => (
        <MetricCard key={m.label} {...m} />
      ))}
    </div>
  );
}
