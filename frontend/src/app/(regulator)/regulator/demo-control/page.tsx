"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { OperationalKeyValuePanel } from "@/components/shared/OperationalDisplay";
import { INITIAL_FEED } from "@/demo/nigeria-intelligence";
import { useCommandStore } from "@/store/command-store";
import { useIntelligenceBusStore } from "@/store/intelligence-bus-store";
import { fetchDemoControlInventory, runDemoControlAction } from "@/services/pilot-readiness";

export default function DemoControlPage() {
  const [inventory, setInventory] = useState<Record<string, unknown> | null>(null);
  const [msg, setMsg] = useState("");

  useEffect(() => {
    fetchDemoControlInventory()
      .then((r) => r.success && setInventory(r.data))
      .catch(() => setInventory(null));
  }, []);

  async function action(name: string) {
    setMsg("");
    if (name === "reset_feed") {
      useCommandStore.setState({ feed: INITIAL_FEED, activityLog: [] });
      useIntelligenceBusStore.setState({ bus: [], nationalThreatIndex: 58 });
      setMsg("DEMO intelligence feed reset (client-side only).");
      return;
    }
    const r = await runDemoControlAction(name);
    setMsg(r.message);
    fetchDemoControlInventory().then((res) => res.success && setInventory(res.data));
  }

  return (
    <RegulatorGuard>
      <CommandShell title="Pilot Demo Control">
        <p className="mb-4 rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-2 text-xs text-amber-200">
          DEMO/SIMULATED — Clear only removes records tagged <code className="text-amber-100">pilot_demo</code> or{" "}
          <code className="text-amber-100">DEMO-</code> incidents.
        </p>
        <GlassPanel title="Demo inventory" className="mb-6">
          <OperationalKeyValuePanel data={inventory} emptyMessage="Loading demo inventory…" />
        </GlassPanel>
        <div className="flex flex-wrap gap-2">
          {[
            ["seed_products", "Seed demo products"],
            ["seed_incident", "Seed demo incident"],
            ["clear_demo", "Clear tagged demo data"],
            ["reset_feed", "Reset sim intelligence feed"],
          ].map(([id, label]) => (
            <button
              key={id}
              type="button"
              onClick={() => action(id)}
              className="rounded-lg border border-sovereign-600 px-3 py-2 text-xs hover:border-sovereign-accent"
            >
              {label}
            </button>
          ))}
        </div>
        {msg && <p className="mt-4 text-sm text-sovereign-accent">{msg}</p>}
      </CommandShell>
    </RegulatorGuard>
  );
}
