"use client";

import { useCallback, useEffect, useState } from "react";
import clsx from "clsx";
import { fetchNotificationCenter, markNotificationRead } from "@/services/notifications";

type NotificationRow = {
  id: string;
  title: string;
  body: string;
  severity: string;
  notification_type: string;
  is_read: boolean;
  created_at: string;
};

const severityClass: Record<string, string> = {
  INFO: "border-slate-600/50 bg-slate-800/40",
  WARNING: "border-amber-500/40 bg-amber-500/10",
  CRITICAL: "border-red-500/40 bg-red-500/10",
  SUCCESS: "border-emerald-500/40 bg-emerald-500/10",
};

export function NotificationCenter({ compact = false }: { compact?: boolean }) {
  const [open, setOpen] = useState(false);
  const [rows, setRows] = useState<NotificationRow[]>([]);
  const [unread, setUnread] = useState(0);
  const [loading, setLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      const res = await fetchNotificationCenter();
      setRows((res.data?.notifications as NotificationRow[]) ?? []);
      setUnread(res.data?.unread ?? 0);
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    load();
    const t = setInterval(load, 60000);
    return () => clearInterval(t);
  }, [load]);

  async function onMarkRead(id: string) {
    await markNotificationRead(id);
    await load();
  }

  if (compact) {
    return (
        <div className="relative">
          <button
            type="button"
            onClick={() => setOpen(!open)}
            className="relative rounded-lg border border-sovereign-700 px-3 py-2 text-xs text-slate-300 hover:bg-sovereign-800"
            aria-label="Notifications"
          >
            Notifications
            {unread > 0 && (
              <span className="absolute -right-1 -top-1 flex h-4 min-w-4 items-center justify-center rounded-full bg-red-500 px-1 text-[10px] text-white">
                {unread > 9 ? "9+" : unread}
              </span>
            )}
          </button>
          {open && (
            <div className="absolute right-0 top-full z-50 mt-2 w-80 rounded-xl border border-sovereign-700 bg-sovereign-900 p-3 shadow-xl">
              <NotificationList
                rows={rows}
                loading={loading}
                onMarkRead={onMarkRead}
                onClose={() => setOpen(false)}
              />
            </div>
          )}
        </div>
    );
  }

  return (
    <div className="rounded-xl border border-sovereign-800 bg-sovereign-900/60 p-4">
      <PanelHeader unread={unread} loading={loading} onRefresh={load} />
      <NotificationList rows={rows} loading={loading} onMarkRead={onMarkRead} />
    </div>
  );
}

function PanelHeader({
  unread,
  loading,
  onRefresh,
}: {
  unread: number;
  loading: boolean;
  onRefresh: () => void;
}) {
  return (
    <div className="mb-3 flex items-center justify-between">
      <h3 className="text-sm font-semibold text-white">Notification center</h3>
      <div className="flex items-center gap-3">
        {unread > 0 && <span className="text-xs text-amber-300">{unread} unread</span>}
        <button type="button" onClick={onRefresh} className="text-xs text-sovereign-accent hover:underline">
          {loading ? "Loading…" : "Refresh"}
        </button>
      </div>
    </div>
  );
}

function NotificationList({
  rows,
  loading,
  onMarkRead,
  onClose,
}: {
  rows: NotificationRow[];
  loading: boolean;
  onMarkRead: (id: string) => void;
  onClose?: () => void;
}) {
  if (loading && rows.length === 0) {
    return <p className="text-xs text-slate-500">Loading notifications…</p>;
  }
  if (rows.length === 0) {
    return <p className="text-xs text-slate-500">No notifications</p>;
  }
  return (
    <ul className="max-h-72 space-y-2 overflow-y-auto">
      {rows.map((n) => (
        <li
          key={n.id}
          className={clsx(
            "rounded-lg border p-3 text-xs",
            severityClass[n.severity] ?? severityClass.INFO,
            !n.is_read && "ring-1 ring-sovereign-accent/30"
          )}
        >
          <div className="flex items-start justify-between gap-2">
            <div>
              <p className="font-medium text-slate-100">{n.title}</p>
              {n.body && <p className="mt-1 text-slate-400">{n.body}</p>}
              <p className="mt-1 text-[10px] text-slate-500">{new Date(n.created_at).toLocaleString()}</p>
            </div>
            {!n.is_read && (
              <button
                type="button"
                onClick={() => {
                  onMarkRead(n.id);
                  onClose?.();
                }}
                className="shrink-0 text-sovereign-accent hover:underline"
              >
                Mark read
              </button>
            )}
          </div>
        </li>
      ))}
    </ul>
  );
}
