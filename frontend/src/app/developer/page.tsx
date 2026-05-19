"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalKeyValuePanel } from "@/components/shared/OperationalDisplay";
import { fetchDeveloperOverview } from "@/services/developer";

export default function DeveloperPortalPage() {
  const [overview, setOverview] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    fetchDeveloperOverview()
      .then((r) => r.success && setOverview(r.data))
      .catch(() => setOverview(null));
  }, []);

  return (
    <RegulatorGuard>
      <div className="min-h-screen bg-sovereign-950 text-slate-100">
        <header className="border-b border-sovereign-800 px-6 py-4">
          <Link href="/regulator" className="text-xs text-sovereign-accent">
            ← National Command
          </Link>
          <h1 className="mt-2 text-2xl font-semibold">Public API · Developer Portal</h1>
        </header>
        <main className="mx-auto max-w-3xl p-6">
          <div className="glass-panel rounded-xl border border-sovereign-800 p-4">
            {overview ? (
              <OperationalKeyValuePanel data={overview} title="Developer overview" />
            ) : (
              <p className="text-xs text-slate-500">Loading developer overview…</p>
            )}
          </div>
          <p className="mt-4 text-sm text-slate-500">
            API keys, scopes, and audit logs — foundation for GS1 and government integrations.
          </p>
        </main>
      </div>
    </RegulatorGuard>
  );
}
