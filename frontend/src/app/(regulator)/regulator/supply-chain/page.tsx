"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchCustodyExplorer, fetchShipmentTimeline } from "@/services/supply-chain-intelligence";

export default function SupplyChainPage() {
  const [shipments, setShipments] = useState<unknown[]>([]);
  const [custody, setCustody] = useState<unknown[]>([]);

  useEffect(() => {
    Promise.all([fetchShipmentTimeline(), fetchCustodyExplorer()]).then(([s, c]) => {
      setShipments(s.data?.shipments ?? []);
      setCustody(c.data?.transfers ?? []);
    });
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Supply chain intelligence">
        <p className="mb-4 text-sm text-slate-400">Shipment lifecycle & custody explorer</p>
        <h3 className="mb-2 text-sm font-semibold text-slate-300">Active shipments</h3>
        <ul className="mb-6 space-y-2">
          {(shipments as { tracking_number: string; lifecycle_status: string; route_anomaly_score: number }[]).map(
            (s) => (
              <li key={s.tracking_number} className="rounded-lg border border-sovereign-800 px-3 py-2 text-xs">
                {s.tracking_number} · {s.lifecycle_status} · anomaly {s.route_anomaly_score}
              </li>
            )
          )}
        </ul>
        <h3 className="mb-2 text-sm font-semibold text-slate-300">Custody transfers</h3>
        <ul className="space-y-2">
          {(custody as { audit_reference: string; transaction_type: string }[]).slice(0, 15).map((t) => (
            <li key={t.audit_reference} className="text-xs text-slate-400">
              {t.transaction_type} · {t.audit_reference.slice(0, 8)}…
            </li>
          ))}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
