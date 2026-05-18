"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { fetchNotificationCenter } from "@/services/notifications";

export default function NotificationCenterPage() {
  const [items, setItems] = useState<unknown[]>([]);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    fetchNotificationCenter()
      .then((r) => {
        if (r.success) {
          setItems(r.data.notifications ?? []);
          setUnread(r.data.unread ?? 0);
        }
      })
      .catch(() => setItems([]));
  }, []);

  return (
    <RegulatorGuard>
      <CommandShell title="National Notification Center">
        <p className="mb-4 text-sm text-slate-500">{unread} unread · push, email, SMS, recall & enforcement stubs</p>
        <ul className="space-y-2">
          {items.map((n, i) => (
            <li key={i} className="glass-panel rounded-lg border border-sovereign-800 px-4 py-3 text-sm">
              <pre className="text-xs text-slate-400">{JSON.stringify(n, null, 2)}</pre>
            </li>
          ))}
          {items.length === 0 && <li className="text-slate-600">No notifications — sign in as regulator.</li>}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
