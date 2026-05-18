"use client";

import { FormEvent, useMemo, useState } from "react";
import Link from "next/link";
import {
  publicVerify,
  reportCounterfeit,
  fetchPublicRecalls,
  fetchTrustedPharmacies,
} from "@/services/citizen";

type UiOutcome =
  | "AUTHENTIC"
  | "SUSPICIOUS"
  | "RECALLED"
  | "EXPIRED"
  | "DUPLICATE_SCAN"
  | "INVALID_SERIAL"
  | "ERROR"
  | "IDLE";

function deriveUiOutcome(res: Record<string, unknown>): UiOutcome {
  if (res.outcome === "error") return "ERROR";
  const o = String(res.outcome ?? "").toLowerCase();
  if (res.duplicate_scan_warning === true) return "DUPLICATE_SCAN";
  if (o.includes("recall")) return "RECALLED";
  if (o.includes("expired")) return "EXPIRED";
  if (o.includes("invalid") || o.includes("unknown")) return "INVALID_SERIAL";
  if (o.includes("suspicious") || o.includes("counterfeit")) return "SUSPICIOUS";
  if (res.is_authentic === true || o.includes("authentic")) return "AUTHENTIC";
  return "SUSPICIOUS";
}

const OUTCOME_STYLES: Record<Exclude<UiOutcome, "IDLE">, string> = {
  AUTHENTIC: "border-emerald-500/50 bg-emerald-500/10 text-emerald-100",
  SUSPICIOUS: "border-amber-500/50 bg-amber-500/10 text-amber-100",
  RECALLED: "border-rose-500/50 bg-rose-500/15 text-rose-100",
  EXPIRED: "border-slate-500/50 bg-slate-800/60 text-slate-200",
  DUPLICATE_SCAN: "border-violet-500/50 bg-violet-500/10 text-violet-100",
  INVALID_SERIAL: "border-red-500/50 bg-red-500/10 text-red-100",
  ERROR: "border-red-500/40 bg-red-950/40 text-red-200",
};

export default function CitizenPortalPage() {
  const [serial, setSerial] = useState("");
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [reportMsg, setReportMsg] = useState("");
  const [pharmacyComplaint, setPharmacyComplaint] = useState("");
  const [adverseText, setAdverseText] = useState("");
  const [recalls, setRecalls] = useState<unknown[]>([]);
  const [pharmacies, setPharmacies] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(false);
  const [demoNote, setDemoNote] = useState<string | null>(null);

  const uiOutcome = useMemo(() => (result ? deriveUiOutcome(result) : "IDLE"), [result]);

  async function onVerify(e: FormEvent) {
    e.preventDefault();
    setLoading(true);
    setDemoNote(null);
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
    <div className="min-h-screen bg-gradient-to-b from-sovereign-950 via-sovereign-950 to-sovereign-900 text-slate-100">
      <header className="sticky top-0 z-10 border-b border-sovereign-800/80 bg-sovereign-950/90 px-4 py-4 backdrop-blur-md sm:px-6">
        <Link href="/login" className="text-[10px] uppercase tracking-widest text-sovereign-accent">
          Operator login
        </Link>
        <h1 className="mt-1 text-xl font-semibold sm:text-2xl">Citizen verification</h1>
        <p className="mt-1 max-w-xl text-xs text-slate-500">
          Mobile-first national authenticity check — scan QR, barcode, or enter serial manually.
        </p>
      </header>

      <main className="mx-auto max-w-lg px-4 py-6 sm:px-6 sm:py-10">
        <form
          onSubmit={onVerify}
          className="glass-panel rounded-2xl border border-sovereign-800 p-4 shadow-xl sm:p-6"
        >
          <label className="text-sm text-slate-400">
            Serial / QR payload / barcode
            <input
              className="mt-2 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 px-3 py-3 font-mono text-sm"
              value={serial}
              onChange={(e) => setSerial(e.target.value)}
              placeholder="NG-NPTTE-…"
              inputMode="text"
              autoComplete="off"
              required
            />
          </label>
          <button
            type="submit"
            disabled={loading}
            className="neon-alert mt-4 w-full rounded-lg bg-emerald-600 py-3 text-sm font-medium text-white disabled:opacity-50"
          >
            {loading ? "Verifying…" : "Verify authenticity"}
          </button>
        </form>

        {result && uiOutcome !== "IDLE" && (
          <div
            className={`mt-6 rounded-2xl border p-4 text-sm sm:p-5 ${
              OUTCOME_STYLES[uiOutcome in OUTCOME_STYLES ? uiOutcome : "ERROR"]
            }`}
          >
            <p className="text-[10px] uppercase tracking-wider text-slate-500">National registry</p>
            <p className="mt-2 text-lg font-semibold tracking-wide">{uiOutcome.replace("_", " ")}</p>
            <p className="mt-1 text-xs capitalize text-slate-300">
              API outcome: {String(result.outcome ?? "unknown")}
            </p>
            {result.result != null && result.result !== "" && (
              <p className="mt-1 text-xs text-slate-400">Status: {String(result.result)}</p>
            )}
            {uiOutcome === "DUPLICATE_SCAN" && (
              <p className="mt-2 text-xs text-violet-200">Elevated scan activity detected on this serial.</p>
            )}
            <p className="mt-3 text-slate-200">{String((result as { message?: string }).message ?? "")}</p>
            {Boolean(result.safety_message) && typeof result.safety_message === "string" && (
              <p className="mt-3 border-t border-white/10 pt-3 text-slate-100">{String(result.safety_message)}</p>
            )}
            {Boolean(result.next_action) && typeof result.next_action === "string" && (
              <p className="mt-2 text-xs text-sovereign-accent">Next: {String(result.next_action)}</p>
            )}
            {result.counterfeit_probability != null && (
              <p className="mt-2 text-xs text-amber-200">
                Counterfeit probability (AI): {String(result.counterfeit_probability)}%
              </p>
            )}
            {(Boolean(result.product) || Boolean(result.manufacturer) || Boolean(result.batch_number)) && (
              <ul className="mt-4 space-y-1 border-t border-white/10 pt-3 text-xs text-slate-300">
                {Boolean(result.manufacturer) && <li>Manufacturer: {String(result.manufacturer)}</li>}
                {Boolean(result.batch_number) && <li>Batch: {String(result.batch_number)}</li>}
                {Boolean(result.expiry_date) && <li>Expiry: {String(result.expiry_date)}</li>}
                {Boolean(result.lifecycle_status) && (
                  <li>Recall / lifecycle: {String(result.lifecycle_status)}</li>
                )}
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

        <section className="mt-10 space-y-6">
          <div className="glass-panel rounded-2xl border border-sovereign-800 p-4 sm:p-5">
            <h2 className="text-sm font-semibold text-white">Counterfeit reporting</h2>
            <p className="mt-1 text-xs text-slate-500">Submits to national public API when available.</p>
            <textarea
              className="mt-3 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 p-3 text-sm"
              rows={3}
              placeholder="Describe what you found…"
              value={reportMsg}
              onChange={(e) => setReportMsg(e.target.value)}
            />
            <button
              type="button"
              className="mt-3 w-full rounded-lg border border-emerald-700/50 bg-emerald-950/30 py-2 text-sm text-emerald-200"
              onClick={() =>
                reportCounterfeit({ description: reportMsg, serial_number: serial }).then(() =>
                  setDemoNote("Counterfeit report accepted by API (or queued).")
                )
              }
            >
              Submit report
            </button>
          </div>

          <div className="glass-panel rounded-2xl border border-sovereign-800 p-4 sm:p-5">
            <h2 className="text-sm font-semibold text-white">Pharmacy complaint</h2>
            <p className="mt-1 text-xs text-slate-500">
              Captured for regulator triage — extends counterfeit endpoint with structured prefix when submitted.
            </p>
            <textarea
              className="mt-3 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 p-3 text-sm"
              rows={3}
              placeholder="Pharmacy name, location, issue…"
              value={pharmacyComplaint}
              onChange={(e) => setPharmacyComplaint(e.target.value)}
            />
            <button
              type="button"
              className="mt-3 w-full rounded-lg border border-sky-700/50 bg-sky-950/30 py-2 text-sm text-sky-200"
              onClick={() =>
                reportCounterfeit({
                  description: `[PHARMACY_COMPLAINT] ${pharmacyComplaint}`,
                  serial_number: serial || undefined,
                }).then(() => setDemoNote("Pharmacy complaint logged for national desk review."))
              }
            >
              Submit complaint
            </button>
          </div>

          <div className="glass-panel rounded-2xl border border-sovereign-800 p-4 sm:p-5">
            <h2 className="text-sm font-semibold text-white">Adverse reaction notice</h2>
            <p className="mt-1 text-xs text-slate-500">
              Rapid triage stub — in production this would route to pharmacovigilance intake.
            </p>
            <textarea
              className="mt-3 w-full rounded-lg border border-sovereign-700 bg-sovereign-950 p-3 text-sm"
              rows={3}
              placeholder="Symptoms, timing, suspected product…"
              value={adverseText}
              onChange={(e) => setAdverseText(e.target.value)}
            />
            <button
              type="button"
              className="mt-3 w-full rounded-lg border border-rose-700/50 bg-rose-950/30 py-2 text-sm text-rose-100"
              onClick={() => {
                setDemoNote(
                  adverseText.trim()
                    ? "Adverse notice captured locally for demo — wire to PV API in production."
                    : "Add details before submitting."
                );
              }}
            >
              Submit adverse notice (demo)
            </button>
          </div>
        </section>

        {demoNote && <p className="mt-6 text-center text-xs text-sovereign-accent">{demoNote}</p>}

        <section className="mt-10 flex flex-wrap gap-3">
          <button
            type="button"
            className="rounded-full border border-sovereign-700 px-4 py-2 text-xs text-sovereign-accent"
            onClick={() => fetchPublicRecalls().then((r) => setRecalls(r.data.recalls ?? []))}
          >
            View recalls
          </button>
          <button
            type="button"
            className="rounded-full border border-sovereign-700 px-4 py-2 text-xs text-sovereign-accent"
            onClick={() => fetchTrustedPharmacies().then((r) => setPharmacies(r.data.pharmacies ?? []))}
          >
            Trusted pharmacies
          </button>
        </section>
        {(recalls.length > 0 || pharmacies.length > 0) && (
          <pre className="mt-4 max-h-64 overflow-auto rounded-xl bg-sovereign-950 p-3 text-[10px] text-slate-400">
            {JSON.stringify({ recalls, pharmacies }, null, 2)}
          </pre>
        )}
      </main>
    </div>
  );
}
