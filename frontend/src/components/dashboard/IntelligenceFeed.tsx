"use client";

import clsx from "clsx";
import { useCommandStore } from "@/store/command-store";
import { openExplorerFromContext } from "@/services/explorer-routing";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

const severityColor = {
  low: "border-slate-600",
  medium: "border-amber-500/50",
  high: "border-orange-500/60",
  critical: "border-red-500/70",
};

export function IntelligenceFeed() {
  const feed = useCommandStore((s) => s.feed);
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);

  const mapFeedContext = (e: { type: string }) => {
    if (e.type === "customs") return "customs";
    if (e.type === "shortage") return "open_alerts";
    if (e.type === "recall") return "recalls";
    return "counterfeit_detections";
  };

  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 shadow-lg">
      <div className="border-b border-sovereign-800 px-4 py-3">
        <h3 className="text-sm font-semibold text-white">Live intelligence feed</h3>
        <p className="text-[10px] text-slate-500">Simulated realtime events (DEMO)</p>
      </div>
      <ul className="max-h-72 overflow-y-auto scroll-smooth">
        {feed.map((e) => (
          <li
            key={e.id}
            role="button"
            tabIndex={0}
            aria-label={`Intelligence item ${e.type}. View details.`}
            onClick={() => void openExplorerFromContext(openDrawer, mapFeedContext(e), e.type)}
            onKeyDown={(ev) => {
              if (ev.key === "Enter" || ev.key === " ") {
                ev.preventDefault();
                void openExplorerFromContext(openDrawer, mapFeedContext(e), e.type);
              }
            }}
            className={clsx(
              "cursor-pointer border-l-2 border-b border-sovereign-800/80 px-4 py-3 text-sm outline-none transition hover:bg-sovereign-800/40 focus:ring-2 focus:ring-sovereign-accent/30",
              severityColor[e.severity]
            )}
          >
            <span className="text-[10px] uppercase text-slate-500">{e.type}</span>
            <p className="mt-0.5 text-slate-200">{e.message}</p>
            <time className="mt-1 block text-[10px] text-slate-600">
              {new Date(e.at).toLocaleTimeString("en-NG")}
            </time>
          </li>
        ))}
      </ul>
    </div>
  );
}
