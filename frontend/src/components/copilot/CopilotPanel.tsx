"use client";

import { useCallback, useMemo, useState } from "react";
import clsx from "clsx";
import {
  copilotDraftEnforcementNote,
  copilotExplainRisk,
  copilotGenerateBriefing,
  copilotRecommendActions,
  copilotSummariseInvestigation,
  type CopilotPayload,
  type CopilotRequest,
} from "@/services/copilot";

type ActionDef = {
  id: string;
  label: string;
  run: (body: CopilotRequest) => ReturnType<typeof copilotExplainRisk>;
};

const DEFAULT_ACTIONS: ActionDef[] = [
  { id: "explain", label: "Explain this risk", run: copilotExplainRisk },
  { id: "briefing", label: "Generate briefing", run: copilotGenerateBriefing },
  { id: "recommend", label: "Recommend action", run: copilotRecommendActions },
  { id: "investigation", label: "Summarise investigation", run: copilotSummariseInvestigation },
  { id: "note", label: "Draft enforcement note", run: copilotDraftEnforcementNote },
];

export function CopilotPanel({
  entityType,
  entityId,
  contextKey,
  selectedRecordIds,
  compact = false,
  extraActions,
  onCreateTask,
}: {
  entityType?: string;
  entityId?: string;
  contextKey?: string;
  selectedRecordIds?: string[];
  compact?: boolean;
  extraActions?: ActionDef[];
  onCreateTask?: (suggestion: string) => void;
}) {
  const [loading, setLoading] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CopilotPayload | null>(null);

  const baseBody = useMemo<CopilotRequest>(
    () => ({
      entity_type: entityType,
      entity_id: entityId,
      context_key: contextKey,
      selected_record_ids: selectedRecordIds,
    }),
    [entityType, entityId, contextKey, selectedRecordIds]
  );

  const run = useCallback(
    async (action: ActionDef) => {
      setLoading(action.id);
      setError(null);
      try {
        const res = await action.run(baseBody);
        if (!res.success || !res.data) {
          setError(("message" in res && res.message) || "Copilot request failed");
          setResult(null);
          return;
        }
        setResult(res.data);
      } catch (e) {
        setError(e instanceof Error ? e.message : "Request failed");
        setResult(null);
      } finally {
        setLoading(null);
      }
    },
    [baseBody]
  );

  const actions = extraActions ?? DEFAULT_ACTIONS;

  return (
    <section
      className={clsx(
        "rounded-lg border border-sovereign-700/80 bg-sovereign-900/40",
        compact ? "p-2" : "p-3"
      )}
    >
      <h4 className="text-[11px] font-semibold uppercase tracking-wide text-sovereign-accent">
        Sovereign AI Copilot
      </h4>
      <p className="mt-1 text-[10px] text-slate-500">Runs only when you click — never automatic.</p>
      <div className="mt-2 flex flex-wrap gap-1.5">
        {actions.map((a) => (
          <button
            key={a.id}
            type="button"
            disabled={Boolean(loading)}
            onClick={() => void run(a)}
            className="rounded border border-sovereign-600 px-2 py-1 text-[10px] text-slate-200 transition hover:border-sovereign-accent hover:text-sovereign-accent disabled:opacity-50"
          >
            {loading === a.id ? "Working…" : a.label}
          </button>
        ))}
      </div>
      {error && <p className="mt-2 text-[11px] text-red-300">{error}</p>}
      {result && (
        <div className="mt-3 space-y-2 rounded border border-sovereign-800 bg-sovereign-950/80 p-2 text-[11px]">
          <p className="font-medium text-amber-200/90">{result.disclaimer}</p>
          {result.cached && <p className="text-slate-600">Cached insight (10 min)</p>}
          <p className="text-slate-500">
            Source: {result.source} · Urgency: {result.urgency} · Confidence:{" "}
            {Math.round((result.confidence ?? 0) * 100)}%
          </p>
          <p className="font-semibold text-white">{result.summary}</p>
          <p className="whitespace-pre-wrap text-slate-300">{result.reasoning}</p>
          {result.recommended_actions?.length > 0 && (
            <ul className="list-disc space-y-0.5 pl-4 text-slate-400">
              {result.recommended_actions.map((act) => (
                <li key={act}>{act}</li>
              ))}
            </ul>
          )}
          {result.source_records?.length > 0 && (
            <div>
              <p className="mb-1 text-slate-500">Source records</p>
              <ul className="max-h-24 space-y-1 overflow-auto text-slate-500">
                {result.source_records.map((r, i) => (
                  <li key={String(r.id ?? i)}>
                    {String(r.title ?? "Record")} — {String(r.organisation ?? "")}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {onCreateTask && result.recommended_actions?.[0] && (
            <button
              type="button"
              className="text-sovereign-accent hover:underline"
              onClick={() => onCreateTask(result.recommended_actions[0])}
            >
              Create task from top recommendation →
            </button>
          )}
          <button
            type="button"
            className="block text-slate-500 hover:text-slate-300"
            onClick={() => {
              void navigator.clipboard?.writeText(
                `${result.summary}\n\n${result.reasoning}\n\nActions:\n${result.recommended_actions?.join("\n") ?? ""}`
              );
            }}
          >
            Copy briefing text
          </button>
        </div>
      )}
    </section>
  );
}
