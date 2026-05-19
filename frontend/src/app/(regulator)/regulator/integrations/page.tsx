"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalKeyValuePanel, OperationalListPanel } from "@/components/shared/OperationalDisplay";
import {
  createExportJob,
  fetchExportJobs,
  fetchIntegrationApiKeys,
  fetchIntegrationHealth,
  fetchWebhookDeliveries,
} from "@/services/integrations";

function StatusBadge({ status }: { status: string }) {
  const tone =
    status === "healthy" || status === "ok"
      ? "bg-emerald-500/15 text-emerald-400"
      : status === "degraded"
        ? "bg-amber-500/15 text-amber-300"
        : "bg-slate-700 text-slate-300";
  return <span className={`rounded px-2 py-0.5 text-[10px] uppercase ${tone}`}>{status || "unknown"}</span>;
}

export default function IntegrationsPage() {
  const [health, setHealth] = useState<Record<string, unknown> | null>(null);
  const [keys, setKeys] = useState<Record<string, unknown>[]>([]);
  const [exports, setExports] = useState<Record<string, unknown>[]>([]);
  const [deliveries, setDeliveries] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    void Promise.allSettled([
      fetchIntegrationHealth().then((r) => setHealth(r.data ?? null)),
      fetchIntegrationApiKeys().then((r) => setKeys((r.data?.keys ?? []) as Record<string, unknown>[])),
      fetchExportJobs().then((r) => setExports((r.data?.exports ?? []) as Record<string, unknown>[])),
      fetchWebhookDeliveries().then((r) => setDeliveries((r.data?.deliveries ?? []) as Record<string, unknown>[])),
    ]);
  }, []);

  async function onExport() {
    await createExportJob({ report_type: "audit", export_format: "csv" });
    const r = await fetchExportJobs();
    setExports((r.data?.exports ?? []) as Record<string, unknown>[]);
  }

  const providers = (health?.providers ?? {}) as Record<string, Record<string, unknown>>;

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
            {!health ? (
              <p className="mt-3 text-xs text-slate-500">Loading providers…</p>
            ) : Object.keys(providers).length === 0 ? (
              <p className="mt-3 text-xs text-slate-500">No provider telemetry yet.</p>
            ) : (
              <ul className="mt-3 space-y-2">
                {Object.entries(providers).map(([name, row]) => (
                  <li
                    key={name}
                    className="flex items-center justify-between rounded border border-sovereign-800 px-3 py-2 text-xs"
                  >
                    <span className="font-medium text-slate-200">{name}</span>
                    <StatusBadge status={String(row.status ?? row.health ?? "unknown")} />
                  </li>
                ))}
              </ul>
            )}
          </section>
          <section className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
            <h2 className="text-sm font-semibold text-white">API keys</h2>
            <OperationalListPanel
              items={keys}
              emptyMessage="No API keys configured."
              renderItem={(row) => (
                <>
                  <p className="font-medium text-slate-200">{String(row.name ?? row.label ?? "Key")}</p>
                  <p className="text-slate-500">Prefix: {String(row.prefix ?? row.key_prefix ?? "—")}</p>
                </>
              )}
            />
          </section>
          <section className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
            <div className="mb-3 flex items-center justify-between">
              <h2 className="text-sm font-semibold text-white">Export center</h2>
              <button
                type="button"
                onClick={onExport}
                className="rounded-lg border border-sovereign-700 px-3 py-1 text-xs text-sovereign-accent hover:bg-sovereign-800"
              >
                Generate audit CSV
              </button>
            </div>
            <OperationalListPanel
              items={exports}
              emptyMessage="No export jobs."
              renderItem={(row) => (
                <>
                  <p className="font-medium text-slate-200">{String(row.report_type ?? "Export")}</p>
                  <p className="text-slate-500">
                    {String(row.export_format ?? "")} · {String(row.status ?? "pending")}
                  </p>
                </>
              )}
            />
          </section>
          <section className="rounded-xl border border-sovereign-800 bg-sovereign-900/50 p-4">
            <h2 className="text-sm font-semibold text-white">Webhook deliveries</h2>
            <OperationalListPanel
              items={deliveries}
              emptyMessage="No webhook deliveries logged."
              renderItem={(row) => (
                <>
                  <p className="font-medium text-slate-200">{String(row.event_type ?? row.endpoint ?? "Delivery")}</p>
                  <p className="text-slate-500">
                    HTTP {String(row.status_code ?? "—")} · {String(row.delivered_at ?? row.created_at ?? "")}
                  </p>
                </>
              )}
            />
          </section>
          {health && (
            <section className="lg:col-span-2">
              <OperationalKeyValuePanel data={health} title="Integration summary" />
            </section>
          )}
        </main>
      </div>
    </RegulatorGuard>
  );
}
