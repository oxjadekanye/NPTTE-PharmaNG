"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { apiRequest } from "@/services/api-client";

export default function NationalAnalyticsPage() {
  const [bundle, setBundle] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    apiRequest<Record<string, unknown>>("/analytics/export-bundle/").then((r) => {
      if (r.success) setBundle(r.data ?? null);
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="National analytics">
        <p className="mb-4 text-sm text-slate-400">Export-ready operational intelligence</p>
        {bundle ? (
          <pre className="max-h-[60vh] overflow-auto rounded-xl border border-sovereign-800 bg-sovereign-950 p-4 text-xs text-slate-400">
            {JSON.stringify(bundle, null, 2)}
          </pre>
        ) : (
          <p className="text-slate-500">Loading analytics bundle…</p>
        )}
      </CommandShell>
    </RegulatorGuard>
  );
}
