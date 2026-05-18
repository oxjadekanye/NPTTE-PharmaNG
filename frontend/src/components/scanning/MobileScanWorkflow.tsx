"use client";

import dynamic from "next/dynamic";
import { FormEvent, useCallback, useState } from "react";
import Link from "next/link";
import { ingestScan, type ScanIngestResult, type ScanType } from "@/services/scanning";
import { useOfflineScanQueue } from "@/store/offline-scan-queue-store";
import { ScanAlertBanner } from "@/components/scanning/ScanAlertBanner";
import { ScanResultCard } from "@/components/scanning/ScanResultCard";
import { OfflineScanQueuePanel } from "@/components/scanning/OfflineScanQueuePanel";

const QrCameraScanner = dynamic(
  () => import("@/components/scanning/QrCameraScanner").then((m) => m.QrCameraScanner),
  { ssr: false, loading: () => <p className="text-center text-xs text-slate-500">Loading scanner…</p> }
);

export type ScanWorkflowConfig = {
  title: string;
  subtitle: string;
  scanType: ScanType;
  actorRole: string;
  requireAuth?: boolean;
  backHref?: string;
};

export function MobileScanWorkflow({
  title,
  subtitle,
  scanType,
  actorRole,
  requireAuth = scanType !== "citizen_verify",
  backHref = "/scan",
}: ScanWorkflowConfig) {
  const [serial, setSerial] = useState("");
  const [cameraOn, setCameraOn] = useState(false);
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanIngestResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const enqueue = useOfflineScanQueue((s) => s.enqueue);
  const ensureDeviceId = useOfflineScanQueue((s) => s.ensureDeviceId);

  const submitScan = useCallback(
    async (value: string) => {
      const trimmed = value.trim();
      if (!trimmed) return;
      setSerial(trimmed);
      setLoading(true);
      setError(null);
      const deviceId = ensureDeviceId();
      const coords =
        typeof navigator !== "undefined" && navigator.geolocation
          ? await new Promise<{ lat?: number; lng?: number }>((resolve) => {
              navigator.geolocation.getCurrentPosition(
                (p) => resolve({ lat: p.coords.latitude, lng: p.coords.longitude }),
                () => resolve({}),
                { timeout: 4000 }
              );
            })
          : {};

      const offline = typeof navigator !== "undefined" && !navigator.onLine;

      try {
        if (offline) {
          enqueue({
            serial_number: trimmed,
            scan_type: scanType,
            actor_role: actorRole,
            device_id: deviceId,
            latitude: coords.lat,
            longitude: coords.lng,
            offline_timestamp: new Date().toISOString(),
          });
          setResult({
            id: "local",
            serial_number: trimmed,
            scan_type: scanType,
            actor_role: actorRole,
            outcome_label: "queued",
            sync_status: "pending",
            risk_score: 0,
            created_at: new Date().toISOString(),
            result: {},
            alerts: {
              recall_alert: false,
              suspicious_scan_alert: false,
              counterfeit_warning: false,
              failed_sync_warning: true,
            },
          });
          return;
        }

        const res = await ingestScan(
          {
            serial_number: trimmed,
            scan_type: scanType,
            actor_role: actorRole,
            device_id: deviceId,
            latitude: coords.lat,
            longitude: coords.lng,
            replay_nonce: `${deviceId}-${Date.now()}`,
          },
          requireAuth
        );
        setResult(res.data);
      } catch (e) {
        const msg = e instanceof Error ? e.message : "Scan failed";
        setError(msg);
        enqueue({
          serial_number: trimmed,
          scan_type: scanType,
          actor_role: actorRole,
          device_id: deviceId,
        });
      } finally {
        setLoading(false);
      }
    },
    [actorRole, enqueue, ensureDeviceId, requireAuth, scanType]
  );

  function onSubmit(e: FormEvent) {
    e.preventDefault();
    void submitScan(serial);
  }

  return (
    <div className="min-h-screen bg-gradient-to-b from-sovereign-950 to-sovereign-900 px-4 py-6 text-slate-100 sm:px-6">
      <Link href={backHref} className="text-[10px] uppercase tracking-widest text-sovereign-accent">
        ← Scan hub
      </Link>
      <h1 className="mt-2 text-2xl font-semibold">{title}</h1>
      <p className="mt-1 max-w-lg text-sm text-slate-500">{subtitle}</p>

      <div className="mx-auto mt-6 max-w-lg space-y-4">
        <OfflineScanQueuePanel />

        <div className="flex gap-2">
          <button
            type="button"
            onClick={() => setCameraOn((v) => !v)}
            className="flex-1 rounded-lg border border-sovereign-700 bg-sovereign-900/80 px-3 py-2 text-sm"
          >
            {cameraOn ? "Hide camera" : "Use camera / QR"}
          </button>
        </div>

        {cameraOn && (
          <QrCameraScanner
            active={cameraOn}
            onScan={(v) => {
              setSerial(v);
              void submitScan(v);
            }}
          />
        )}

        <form onSubmit={onSubmit} className="space-y-3">
          <label className="block text-xs text-slate-400">Serial / barcode / GS1</label>
          <input
            value={serial}
            onChange={(e) => setSerial(e.target.value)}
            placeholder="Enter or paste serial"
            className="w-full rounded-lg border border-sovereign-700 bg-sovereign-950 px-3 py-3 font-mono text-sm"
            autoComplete="off"
          />
          <button
            type="submit"
            disabled={loading || !serial.trim()}
            className="w-full rounded-lg bg-sovereign-accent py-3 text-sm font-semibold text-sovereign-950 disabled:opacity-50"
          >
            {loading ? "Scanning…" : "Submit scan"}
          </button>
        </form>

        {error && <p className="text-sm text-rose-300">{error}</p>}
        {result && (
          <>
            <ScanResultCard result={result} scanType={scanType} />
            <ScanAlertBanner result={result} />
          </>
        )}
      </div>
    </div>
  );
}
