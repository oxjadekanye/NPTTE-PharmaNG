"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import {
  createExportJob,
  fetchExportJobs,
  fetchIntegrationApiKeys,
  fetchIntegrationHealth,
  fetchWebhookDeliveries,
} from "@/services/integrations";

export default function IntegrationsPage() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [keys, setKeys] = useState<unknown[]>([]);
  const [exports, setExports] = useState<unknown[]>([]);
  const [deliveries, setDeliveries] = useState<unknown[]>([]);

  useEffect(() => {
    fetchIntegrationHealth().then((r) => setHealth(r.data ?? null));
    fetchIntegrationApiKeys().then((r) => setKeys(r.data?.keys ?? []));
    fetchExportJobs().then((r) => setExports(r.data?.exports ?? []));
    fetchWebhookDeliveries().then((r) => setDeliveries(r.data?.deliveries ?? []));
  }, []);

  async function onExport() {
    await createExportJob({ report_type: "audit", export_format: "csv" });
    const r = await fetchExportJobs();
    setExports(r.data?.exports ?? []);
  }

  return (
    <RegulatorGuard>
      <div className="min-h-screen bg-sovereign-950 text-slate-100">
        <header className="border-b border-sovereign-800 px-6 py-4">
          <Link href="/regulator" className="text-xs text-sovereign-accent">
            ← National Command
          </Link>
          <h1 className="mt-2 text-2xl font-semibold">Integrations & connectivity</h1>
          <p className="text-sm text-slate-500">Provider health, API keys, webhooks, and exports</p>
        </header>
        <main className="mx-auto grid max-w-6xl gap-6 p-6 lg:grid-cols-2">
          <section className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
            <h2 className="text-sm font-semibold text-white">Provider health</h2>
            <pre className="mt-3 max-h-64 overflow-auto text-xs text-slate-400">
              {health ? JSON.stringify(health.providers, null, 2) : "Loading…"}
            </pre>
          </section>
          <section className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
            <h2 className="text-sm font-semibold text-white">API keys</h2>
            <pre className="mt-3 max-h-64 overflow-auto text-xs text-slate-400">{JSON.stringify(keys, null, 2)}</pre>
          </section>
          <section className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
            <div className="flex items-center justify-between">
              <h2 className="text-sm font-semibold text-white">Export center</h2>
              <button
                type="button"
                onClick={onExport}
                className="rounded-lg border border-sovereign-700 px-3 py-1 text-xs text-sovereign-accent hover:bg-sovereign-800"
              >
                Generate audit CSV
              </button>
            </div>
            <pre className="mt-3 max-h-48 overflow-auto text-xs text-slate-400">{JSON.stringify(exports, null, 2)}</pre>
          </section>
          <section className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
            <h2 className="text-sm font-semibold text-white">Webhook deliveries</h2>
            <pre className="mt-3 max-h-48 overflow-auto text-xs text-slate-400">{JSON.stringify(deliveries, null, 2)}</pre>
          </section>
        </main>
      </div>
    </RegulatorGuard>
  );
}
