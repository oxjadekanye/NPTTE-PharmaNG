"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { publicVerify, reportCounterfeit, fetchPublicRecalls, fetchTrustedPharmacies } from "@/services/citizen";

export default function CitizenPortalPage() {
  const [serial, setSerial] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [reportMsg, setReportMsg] = useState("");
  const [recalls, setRecalls] = useState<unknown[]>([]);
  const [pharmacies, setPharmacies] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(false);

  async function onVerify(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    try {
      const res = await publicVerify({ serial_number: serial });
      setResult({ ...(res.data as Record<string, unknown>), message: res.message });
    } catch {
      setResult({ outcome: "error", message: "Verification failed" });
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sovereign-950 to-sovereign-900 text-slate-100">
      <header className="border-b border-sovereign-800 px-6 py-4">
        <Link href="/" className="text-xs uppercase tracking-widest text-sovereign-accent">
          NPTTE Citizen
        </Link>
        <h1 className="mt-1 text-2xl font-semibold">Verify your medicine</h1>
      </header>
      <main className="mx-auto max-w-lg px-6 py-10">
        <form onSubmit={onVerify} className="rounded-2xl border border-sovereign-800 bg-sovereign-900/80 p-6">
          <label className="text-sm text-slate-400">
            Serial number or scan QR payload
            <input
              className="mt-2 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 px-3 py-3 font-mono text-sm"
              value={serial}
              onChange={(e) => setSerial(e.target.value)}
              placeholder="NG-NPTTE-..."
              required
            />
          </label>
          <button
            type="submit"
            disabled={loading}
            className="mt-4 w-full rounded-lg bg-emerald-600 py-3 font-medium text-white disabled:opacity-50"
          >
            {loading ? "Verifying…" : "Verify authenticity"}
          </button>
        </form>
        {result && (
          <div
            className={`mt-6 rounded-xl border p-4 text-sm ${
              result.is_authentic ? "border-emerald-500/40 bg-emerald-500/10" : "border-red-500/40 bg-red-500/10"
            }`}
          >
            <p className="text-[10px] uppercase tracking-wider text-slate-500">NPTTE national registry (live API)</p>
            <p className="mt-1 font-medium capitalize">Outcome: {String(result.outcome ?? "unknown")}</p>
            {result.result != null && result.result !== "" && (
              <p className="mt-1 text-xs text-slate-400">Status: {String(result.result)}</p>
            )}
            {result.duplicate_scan_warning === true && (
              <p className="mt-2 text-xs text-amber-300">Note: elevated scan activity on this serial.</p>
            )}
            <p className="mt-2 text-slate-300">{String((result as { message?: string }).message ?? "")}</p>
            {Boolean(result.safety_message) && typeof result.safety_message === "string" && (
              <p className="mt-3 border-t border-sovereign-800 pt-3 text-slate-300">{String(result.safety_message)}</p>
            )}
            {Boolean(result.next_action) && typeof result.next_action === "string" && (
              <p className="mt-2 text-xs text-sovereign-accent">Next: {String(result.next_action)}</p>
            )}
            {(Boolean(result.product) || Boolean(result.manufacturer) || Boolean(result.batch_number)) && (
              <ul className="mt-4 space-y-1 border-t border-sovereign-800 pt-3 text-xs text-slate-400">
                {Boolean(result.manufacturer) && <li>Manufacturer: {String(result.manufacturer)}</li>}
                {Boolean(result.batch_number) && <li>Batch: {String(result.batch_number)}</li>}
                {Boolean(result.expiry_date) && <li>Expiry: {String(result.expiry_date)}</li>}
                {Boolean(result.lifecycle_status) && <li>Batch lifecycle: {String(result.lifecycle_status)}</li>}
                {(() => {
                  const p = result.product;
                  if (p != null && typeof p === "object" && "name" in p) {
                    return <li>Product: {String((p as { name?: string }).name ?? "")}</li>;
                  }
                  return null;
                })()}
              </ul>
            )}
          </div>
        )}
        <section className="mt-10">
          <h2 className="text-lg font-medium">Report counterfeit</h2>
          <textarea
            className="mt-2 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 p-3 text-sm"
            rows={3}
            placeholder="Describe what you found…"
            onChange={(e) => setReportMsg(e.target.value)}
          />
          <button
            type="button"
            className="mt-2 rounded border border-sovereign-600 px-4 py-2 text-sm"
            onClick={() =>
              reportCounterfeit({ description: reportMsg, serial_number: serial }).then(() =>
                alert("Report submitted")
              )
            }
          >
            Submit report
          </button>
        </section>
        <section className="mt-8 flex gap-3">
          <button
            type="button"
            className="text-sm text-sovereign-accent"
            onClick={() => fetchPublicRecalls().then((r) => setRecalls(r.data.recalls ?? []))}
          >
            View recalls
          </button>
          <button
            type="button"
            className="text-sm text-sovereign-accent"
            onClick={() => fetchTrustedPharmacies().then((r) => setPharmacies(r.data.pharmacies ?? []))}
          >
            Trusted pharmacies
          </button>
        </section>
        {(recalls.length > 0 || pharmacies.length > 0) && (
          <pre className="mt-4 overflow-auto rounded bg-sovereign-950 p-3 text-xs text-slate-400">
            {JSON.stringify({ recalls, pharmacies }, null, 2)}
          </pre>
        )}
      </main>
    </div>
  );
}
