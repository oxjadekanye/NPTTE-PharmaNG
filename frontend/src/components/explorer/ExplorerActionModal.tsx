"use client";

import { useEffect, useState } from "react";
import clsx from "clsx";
import { readStaffCache, writeStaffCache } from "@/services/auth-session-cache";
import { executeExplorerAction, fetchExplorerStaff } from "@/services/explorer";

export type ExplorerWorkflow = "task" | "ack" | "briefing" | "investigation" | "escalation" | "dismiss";

type Staff = { id: string; full_name: string; role_title?: string; team?: string; region_state?: string };

type Props = {
  open: boolean;
  workflow: ExplorerWorkflow | null;
  entityType: string;
  entityId: string;
  actionId: string;
  actionLabel: string;
  onClose: () => void;
  onSuccess?: (msg: string) => void;
};

export function ExplorerActionModal({
  open,
  workflow,
  entityType,
  entityId,
  actionId,
  actionLabel,
  onClose,
  onSuccess,
}: Props) {
  const [staff, setStaff] = useState<Staff[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [assigneeId, setAssigneeId] = useState("");
  const [priority, setPriority] = useState("high");
  const [dueDate, setDueDate] = useState("");
  const [dueTime, setDueTime] = useState("");
  const [severity, setSeverity] = useState("high");
  const [reason, setReason] = useState("");
  const [briefing, setBriefing] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!open) return;
    setError(null);
    setBriefing(null);
    setTitle(actionLabel);
    const cached = readStaffCache();
    if (cached?.length) setStaff(cached as Staff[]);
    fetchExplorerStaff()
      .then((r) => {
        if (r.success && r.data) {
          const list = (r.data as { staff: Staff[] }).staff ?? [];
          setStaff(list);
          writeStaffCache(list);
        }
      })
      .catch(() => {
        if (!cached?.length) setStaff([]);
      });
  }, [open, actionLabel]);

  if (!open || !workflow) return null;

  const submit = async () => {
    setBusy(true);
    setError(null);
    try {
      const body: Record<string, unknown> = {
        action_id: actionId,
        confirm: workflow !== "ack" && workflow !== "briefing",
        title,
        description,
        priority,
        severity,
        assigned_officer_id: assigneeId || undefined,
        due_date: dueDate || undefined,
        due_time: dueTime || undefined,
        reason,
        rationale: description,
      };
      const res = await executeExplorerAction(entityType, entityId, body);
      if (!res.success) {
        setError(res.message || "Action failed");
        return;
      }
      const data = res.data as Record<string, unknown>;
      if (workflow === "briefing" && data.briefing) {
        setBriefing(data.briefing as Record<string, unknown>);
        onSuccess?.("Briefing generated");
        return;
      }
      onSuccess?.(String(data.message || "Action completed"));
      onClose();
    } catch (e: unknown) {
      setError(e instanceof Error ? e.message : "Request failed");
    } finally {
      setBusy(false);
    }
  };

  return (
    <div className="fixed inset-0 z-[110] flex items-center justify-center bg-black/60 p-4" role="presentation">
      <div
        className="max-h-[90vh] w-full max-w-lg overflow-y-auto rounded-xl border border-sovereign-700 bg-sovereign-950 p-4 shadow-2xl"
        role="dialog"
        aria-modal="true"
      >
        <h3 className="text-sm font-semibold text-white">{actionLabel}</h3>
        <p className="mt-1 text-[10px] text-slate-500">
          {entityType} · {entityId}
        </p>

        {workflow === "briefing" && briefing && (
          <div className="mt-4 space-y-2 rounded border border-sovereign-700 bg-sovereign-900/60 p-3 text-xs text-slate-300">
            <p className="font-medium text-sovereign-accent">AI-assisted briefing</p>
            <p>{String(briefing.summary ?? "")}</p>
            <p className="text-slate-500">{String(briefing.disclaimer ?? "")}</p>
            <ul className="list-disc pl-4">
              {((briefing.recommended_actions as string[]) ?? []).map((a, i) => (
                <li key={i}>{a}</li>
              ))}
            </ul>
            <button type="button" className="mt-2 text-sovereign-accent hover:underline" onClick={onClose}>
              Close
            </button>
          </div>
        )}

        {!(workflow === "briefing" && briefing) && (
          <div className="mt-4 space-y-3 text-xs">
            {(workflow === "task" || workflow === "investigation") && (
              <>
                <label className="block text-slate-400">
                  Title
                  <input
                    value={title}
                    onChange={(e) => setTitle(e.target.value)}
                    className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                  />
                </label>
                <label className="block text-slate-400">
                  Description / rationale
                  <textarea
                    value={description}
                    onChange={(e) => setDescription(e.target.value)}
                    rows={3}
                    className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                  />
                </label>
                <label className="block text-slate-400">
                  Assigned officer
                  <select
                    value={assigneeId}
                    onChange={(e) => setAssigneeId(e.target.value)}
                    className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                  >
                    <option value="">Select officer…</option>
                    {staff.map((s) => (
                      <option key={s.id} value={s.id}>
                        {s.full_name} — {s.role_title} ({s.region_state})
                      </option>
                    ))}
                  </select>
                </label>
              </>
            )}
            {workflow === "task" && (
              <>
                <label className="block text-slate-400">
                  Priority
                  <select
                    value={priority}
                    onChange={(e) => setPriority(e.target.value)}
                    className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                  >
                    <option value="low">Low</option>
                    <option value="normal">Normal</option>
                    <option value="high">High</option>
                    <option value="critical">Critical</option>
                  </select>
                </label>
                <div className="grid grid-cols-2 gap-2">
                  <label className="block text-slate-400">
                    Due date
                    <input
                      type="date"
                      value={dueDate}
                      onChange={(e) => setDueDate(e.target.value)}
                      className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                    />
                  </label>
                  <label className="block text-slate-400">
                    Due time
                    <input
                      type="time"
                      value={dueTime}
                      onChange={(e) => setDueTime(e.target.value)}
                      className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                    />
                  </label>
                </div>
              </>
            )}
            {workflow === "investigation" && (
              <label className="block text-slate-400">
                Severity
                <select
                  value={severity}
                  onChange={(e) => setSeverity(e.target.value)}
                  className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                  <option value="critical">Critical</option>
                </select>
              </label>
            )}
            {workflow === "escalation" && (
              <label className="block text-slate-400">
                Escalation reason
                <textarea
                  value={reason}
                  onChange={(e) => setReason(e.target.value)}
                  rows={3}
                  className="mt-1 w-full rounded border border-sovereign-700 bg-sovereign-900 px-2 py-1.5 text-white"
                />
              </label>
            )}
            {workflow === "ack" && (
              <p className="text-slate-400">Confirm this item has been reviewed. An audit entry will be created.</p>
            )}
            {error && <p className="text-red-300">{error}</p>}
            <div className="flex justify-end gap-2 pt-2">
              <button
                type="button"
                onClick={onClose}
                className="rounded border border-sovereign-700 px-3 py-1.5 text-slate-300 hover:bg-sovereign-800"
              >
                Cancel
              </button>
              <button
                type="button"
                disabled={busy}
                onClick={() => void submit()}
                className={clsx(
                  "rounded bg-sovereign-accent px-3 py-1.5 font-medium text-sovereign-950 disabled:opacity-50"
                )}
              >
                {busy ? "Working…" : workflow === "ack" ? "Confirm" : "Submit"}
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
}
