"use client";

import { useState } from "react";
import { MobileScanWorkflow } from "@/components/scanning/MobileScanWorkflow";
import type { ScanType } from "@/services/scanning";

export default function PharmacyScanPage() {
  const [mode, setMode] = useState<ScanType>("pharmacy_receive");

  return (
    <div>
      <div className="border-b border-sovereign-800 bg-sovereign-950 px-4 py-3 sm:px-6">
        <div className="mx-auto flex max-w-lg gap-2">
          <button
            type="button"
            onClick={() => setMode("pharmacy_receive")}
            className={`flex-1 rounded-lg px-3 py-2 text-xs ${
              mode === "pharmacy_receive"
                ? "bg-sovereign-accent text-sovereign-950"
                : "border border-sovereign-700 text-slate-400"
            }`}
          >
            Serial receipt
          </button>
          <button
            type="button"
            onClick={() => setMode("pharmacy_dispense")}
            className={`flex-1 rounded-lg px-3 py-2 text-xs ${
              mode === "pharmacy_dispense"
                ? "bg-sovereign-accent text-sovereign-950"
                : "border border-sovereign-700 text-slate-400"
            }`}
          >
            Dispensing
          </button>
        </div>
      </div>
      <MobileScanWorkflow
        key={mode}
        title={mode === "pharmacy_receive" ? "Pharmacy serial receipt" : "Pharmacy dispensing"}
        subtitle="Scan inbound stock or dispense to patient. Quarantine suspicious units."
        scanType={mode}
        actorRole="pharmacy"
        backHref="/pharmacy"
      />
    </div>
  );
}
