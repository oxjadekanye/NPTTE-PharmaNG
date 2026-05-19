"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { fetchRegions } from "@/services/command-orchestration";

export default function RegionalHubPage() {
  const [regions, setRegions] = useState<{ key: string; label: string }[]>([]);

  useEffect(() => {
    fetchRegions().then((r) => {
      if (r.success && r.data?.regions) {
        setRegions(r.data.regions as { key: string; label: string }[]);
      }
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Regional command centers">
        <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
          {regions.map((reg) => (
            <Link key={reg.key} href={`/regulator/regions/${reg.key}`}>
              <GlassPanel title={reg.label} subtitle="Regional intelligence">
                <p className="text-xs text-sovereign-accent">Open regional command →</p>
              </GlassPanel>
            </Link>
          ))}
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
