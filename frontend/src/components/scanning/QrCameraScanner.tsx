"use client";

import { useEffect, useId, useRef, useState } from "react";

type Props = {
  onScan: (value: string) => void;
  active?: boolean;
};

export function QrCameraScanner({ onScan, active = true }: Props) {
  const regionId = useId().replace(/:/g, "");
  const scannerRef = useRef<{ stop: () => Promise<void> } | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    if (!active) return;
    let cancelled = false;

    async function start() {
      try {
        const { Html5Qrcode } = await import("html5-qrcode");
        if (cancelled) return;
        const scanner = new Html5Qrcode(regionId);
        scannerRef.current = scanner;
        await scanner.start(
          { facingMode: "environment" },
          { fps: 8, qrbox: { width: 240, height: 240 } },
          (decoded) => {
            onScan(decoded);
          },
          () => {}
        );
        if (!cancelled) {
          setReady(true);
          setError(null);
        }
      } catch (e) {
        if (!cancelled) {
          setError(e instanceof Error ? e.message : "Camera unavailable — use manual entry.");
        }
      }
    }

    start();
    return () => {
      cancelled = true;
      scannerRef.current?.stop().catch(() => {});
      scannerRef.current = null;
    };
  }, [active, onScan, regionId]);

  return (
    <div className="space-y-2">
      <div
        id={regionId}
        className="mx-auto min-h-[220px] max-w-md overflow-hidden rounded-xl border border-sovereign-700 bg-black/40"
      />
      {!ready && !error && (
        <p className="text-center text-xs text-slate-500">Starting camera…</p>
      )}
      {error && <p className="text-center text-xs text-amber-300">{error}</p>}
    </div>
  );
}
