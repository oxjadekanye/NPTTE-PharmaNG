"use client";

import { useState } from "react";
import { GlassPanel } from "@/components/enterprise/GlassPanel";
import { copilotExecutiveBriefing, type CopilotPayload } from "@/services/copilot";

export function ExecutiveAiBriefingPanel({ compact = false }: { compact?: boolean }) {
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<CopilotPayload | null>(null);

  const generate = async () => {
    setLoading(true);
    setError(null);
    try {
      const res = await copilotExecutiveBriefing();
      if (!res.success || !res.data) {
        setError(("message" in res && res.message) || "Briefing unavailable");
        setResult(null);
        return;
      }
      setResult(res.data);
    } catch (e) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setLoading(false);
    }
  };

  const briefingText = result
    ? [
        result.summary,
        "",
        result.reasoning,
        "",
        "Recommended ministerial actions:",
        ...(result.recommended_actions ?? []).map((a) => `• ${a}`),
        "",
        `Urgency: ${result.urgency} · Confidence: ${Math.round((result.confidence ?? 0) * 100)}%`,
        result.disclaimer,
      ].join("\n")
    : "";

  const body = (
    <>
      <p className="text-xs text-slate-500">
        National summary, urgent risks, affected regions, and 24-hour priorities — generated on demand only.
      </p>
      <button
        type="button"
        disabled={loading}
        onClick={() => void generate()}
        className="mt-3 rounded border border-sovereign-600 px-3 py-1.5 text-xs text-sovereign-accent hover:bg-sovereign-800 disabled:opacity-50"
      >
        {loading ? "Generating ministerial briefing…" : "Generate AI executive briefing"}
      </button>
      {error && <p className="mt-2 text-xs text-red-300">{error}</p>}
      {result && (
        <div className="mt-4 space-y-3 text-sm text-slate-200">
          <p className="text-xs text-amber-200/90">{result.disclaimer}</p>
          <p className="font-semibold text-white">{result.summary}</p>
          <p className="whitespace-pre-wrap text-slate-300">{result.reasoning}</p>
          {result.recommended_actions?.length > 0 && (
            <div>
              <p className="mb-1 text-xs uppercase text-slate-500">Recommended ministerial actions</p>
              <ul className="list-disc space-y-1 pl-4 text-slate-400">
                {result.recommended_actions.map((a) => (
                  <li key={a}>{a}</li>
                ))}
              </ul>
            </div>
          )}
          <div className="flex flex-wrap gap-3 text-xs">
            <button
              type="button"
              className="text-sovereign-accent hover:underline"
              onClick={() => void navigator.clipboard?.writeText(briefingText)}
            >
              Copy briefing
            </button>
            <button
              type="button"
              className="text-sovereign-accent hover:underline"
              onClick={() => {
                const blob = new Blob([briefingText], { type: "text/plain" });
                const url = URL.createObjectURL(blob);
                const a = document.createElement("a");
                a.href = url;
                a.download = `nptte-executive-briefing-${new Date().toISOString().slice(0, 10)}.txt`;
                a.click();
                URL.revokeObjectURL(url);
              }}
            >
              Download .txt
            </button>
          </div>
        </div>
      )}
    </>
  );

  if (compact) {
    return <div className="rounded-xl border border-sovereign-800 p-4">{body}</div>;
  }

  return (
    <GlassPanel title="Sovereign AI executive briefing" subtitle="Phase 20B · on-demand" accent="rose">
      {body}
    </GlassPanel>
  );
}
