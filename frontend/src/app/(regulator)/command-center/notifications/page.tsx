"use client";

import { useEffect, useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalKeyValuePanel } from "@/components/shared/OperationalDisplay";
import { openExplorerFromNotification } from "@/services/explorer-routing";
import { fetchNotificationCenter } from "@/services/notifications";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

export default function NotificationCenterPage() {
  const openDrawer = useExplorerDrawerStore((s) => s.openDrawer);
  const [items, setItems] = useState<
    {
      id: string;
      title: string;
      related_entity_type?: string | null;
      related_entity_id?: string | null;
    }[]
  >([]);
  const [unread, setUnread] = useState(0);

  useEffect(() => {
    fetchNotificationCenter()
      .then((r) => {
        if (r.success) {
          setItems((r.data.notifications ?? []) as typeof items);
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
          {items.map((n) => (
            <li key={n.id}>
              <button
                type="button"
                className="glass-panel w-full rounded-lg border border-sovereign-800 px-4 py-3 text-left text-sm transition hover:border-sovereign-accent/40"
                onClick={() => openExplorerFromNotification(openDrawer, n)}
              >
                <p className="font-medium text-white">{n.title}</p>
                <p className="mt-1 text-xs text-sovereign-accent">View operational detail →</p>
              </button>
            </li>
          ))}
          {items.length === 0 && <li className="text-slate-600">No notifications — sign in as regulator.</li>}
        </ul>
      </CommandShell>
    </RegulatorGuard>
  );
}
