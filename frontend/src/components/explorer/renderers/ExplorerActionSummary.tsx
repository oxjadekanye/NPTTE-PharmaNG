"use client";

import { memo } from "react";

export const ExplorerActionSummary = memo(function ExplorerActionSummary({
  actions,
  onSelect,
}: {
  actions: { id: string; label: string; requires_confirm?: boolean }[];
  onSelect: (action: { id: string; label: string; workflow?: string }) => void;
}) {
  if (!actions.length) return null;
  return (
    <ul className="mt-2 space-y-2">
      {actions.map((act) => (
        <li key={act.id}>
          <button
            type="button"
            className="w-full rounded border border-sovereign-700 px-2 py-1.5 text-left text-xs text-sovereign-accent hover:bg-sovereign-800"
            onClick={() => onSelect(act)}
          >
            {act.label}
            {act.requires_confirm ? (
              <span className="ml-2 text-[10px] text-amber-400">Confirm required</span>
            ) : null}
          </button>
        </li>
      ))}
    </ul>
  );
});
