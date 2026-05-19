"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import {
  acceptRecommendation,
  fetchEnforcementCases,
  fetchEnforcementRecommendations,
  fetchEnforcementTimeline,
} from "@/services/sovereign-intelligence";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

export default function EnforcementBoardPage() {
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);
  const [cases, setCases] = useState<Record<string, unknown>[]>([]);
  const [recs, setRecs] = useState<Record<string, unknown>[]>([]);
  const [timeline, setTimeline] = useState<Record<string, unknown>[]>([]);

  const reload = () => {
    fetchEnforcementCases().then((r) => setCases((r.data?.cases as Record<string, unknown>[]) ?? []));
    fetchEnforcementRecommendations().then((r) =>
      setRecs((r.data?.recommendations as Record<string, unknown>[]) ?? [])
    );
    fetchEnforcementTimeline().then((r) => setTimeline((r.data?.timeline as Record<string, unknown>[]) ?? []));
  };

  useEffect(() => {
    reload();
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="Enforcement">
        <div className="mb-4 flex flex-wrap gap-3 text-xs">
          <Link href="/regulator/enforcement/cases" className="text-sovereign-accent hover:underline">
            Case board →
          </Link>
          <Link href="/regulator/intelligence" className="text-sovereign-accent hover:underline">
            Intelligence →
          </Link>
        </div>
        <div className="grid gap-4 lg:grid-cols-2">
          <GlassPanel title="Recommendations" accent="amber">
            <ul className="space-y-2 text-xs">
              {recs.map((rec) => (
                <li key={String(rec.id)} className="rounded border border-sovereign-700/50 p-2">
                  <button
                    type="button"
                    className="w-full text-left outline-none transition hover:text-sovereign-accent"
                    onClick={() =>
                      openDrawer({
                        entityType: "enforcement_recommendation",
                        entityId: String(rec.id),
                        title: String(rec.title),
                      })
                    }
                  >
                    <p className="font-medium text-slate-200">{String(rec.title)}</p>
                    <p className="text-slate-500">
                      {String(rec.recommendation_type)} · {String(rec.severity)}
                    </p>
                  </button>
                  <button
                    type="button"
                    className="mt-2 text-sovereign-accent"
                    onClick={() => acceptRecommendation(String(rec.id)).then(reload)}
                  >
                    Accept
                  </button>
                </li>
              ))}
              {recs.length === 0 && <li className="text-slate-500">No pending recommendations</li>}
            </ul>
          </GlassPanel>
          <GlassPanel title="Open cases">
            <ul className="space-y-2 text-xs">
              {cases.map((c) => (
                <li key={String(c.id)} className="rounded border border-sovereign-700/50 p-2">
                  <Link
                    href={`/regulator/explorer/enforcement_case/${encodeURIComponent(String(c.id))}`}
                    className="block font-medium text-slate-200 hover:text-sovereign-accent"
                  >
                    {String(c.title)}
                  </Link>
                  <p className="text-slate-500">
                    {String(c.case_reference)} · {String(c.case_status)} · {String(c.severity)}
                  </p>
                  <button
                    type="button"
                    className="mt-1 text-[10px] text-sovereign-accent hover:underline"
                    onClick={() =>
                      openDrawer({
                        entityType: "enforcement_case",
                        entityId: String(c.id),
                        title: String(c.title),
                      })
                    }
                  >
                    Quick view
                  </button>
                </li>
              ))}
            </ul>
          </GlassPanel>
          <GlassPanel title="Timeline" className="lg:col-span-2">
            <ul className="max-h-64 space-y-1 overflow-y-auto text-xs text-slate-400">
              {timeline.map((e) => (
                <li key={String(e.id)}>
                  <button
                    type="button"
                    className="w-full rounded px-1 text-left text-slate-400 outline-none hover:bg-sovereign-800/50 hover:text-slate-200"
                    onClick={() => {
                      if (!e.case_id) return;
                      openDrawer({
                        entityType: "enforcement_case",
                        entityId: String(e.case_id),
                        title: String(e.summary),
                      });
                    }}
                  >
                    [{String(e.entry_type)}] {String(e.summary)}
                  </button>
                </li>
              ))}
            </ul>
          </GlassPanel>
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
