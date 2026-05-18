"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { fetchCounterfeitClusters } from "@/services/sovereign-intelligence";

export default function IntelligenceClustersPage() {
  const [clusters, setClusters] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    fetchCounterfeitClusters().then((r) => setClusters((r.data?.clusters as Record<string, unknown>[]) ?? []));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Counterfeit clusters">
        <Link href="/regulator/intelligence" className="text-xs text-sovereign-accent">
          ← Intelligence
        </Link>
        <div className="mt-6 grid gap-4 md:grid-cols-2">
          {clusters.map((c) => (
            <GlassPanel key={String(c.cluster_code)} title={String(c.cluster_code)} accent="rose">
              <p className="text-xs text-slate-400">Region: {String(c.region_state || "—")}</p>
              <p className="text-xs text-slate-400">
                Scans {String(c.scan_count)} · Suspicious {String(c.suspicious_count)} · Confidence{" "}
                {String(c.confidence)}%
              </p>
            </GlassPanel>
          ))}
          {clusters.length === 0 && <p className="text-sm text-slate-500">No open clusters detected.</p>}
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
