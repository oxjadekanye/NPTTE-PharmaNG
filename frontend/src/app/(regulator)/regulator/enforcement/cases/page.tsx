"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { fetchEnforcementCases } from "@/services/sovereign-intelligence";

export default function EnforcementCasesPage() {
  const [cases, setCases] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    fetchEnforcementCases().then((r) => setCases((r.data?.cases as Record<string, unknown>[]) ?? []));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Enforcement cases">
        <Link href="/regulator/enforcement" className="text-xs text-sovereign-accent">
          ← Enforcement
        </Link>
        <div className="mt-6 grid gap-3">
          {cases.map((c) => (
            <GlassPanel key={String(c.id)} title={String(c.title)} subtitle={String(c.case_reference)}>
              <p className="text-xs text-slate-400">
                Status {String(c.case_status)} · Severity {String(c.severity)}
              </p>
            </GlassPanel>
          ))}
          {cases.length === 0 && <p className="text-sm text-slate-500">No enforcement cases.</p>}
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
