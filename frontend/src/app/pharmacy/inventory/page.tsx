"use client";

import { useEffect, useState } from "react";
import { apiRequest } from "@/services/api-client";

export default function PharmacyInventoryPage() {
  const [items, setItems] = useState<unknown[]>([]);
  const [sync, setSync] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    apiRequest<{ count: number; items: unknown[] }>("/pharmacies/availability/").then((r) => {
      if (r.success && r.data) setItems((r.data as { items?: unknown[] }).items ?? []);
    });
    apiRequest<Record<string, unknown>>("/pharmacies/inventory/sync/").then((r) => {
      if (r.success) setSync(r.data ?? null);
    });
  }, []);

  return (
    <div className="min-h-screen bg-sovereign-950 px-4 py-8 text-white">
      <p className="text-xs uppercase tracking-widest text-sky-400">Pharmacy operations</p>
      <h1 className="mt-2 text-2xl font-bold">Live inventory</h1>
      {sync && (
        <p className="mt-2 text-sm text-slate-400">
          {String(sync.total_skus)} SKUs · {String(sync.low_stock_count)} low stock ·{" "}
          {String(sync.disclaimer)}
        </p>
      )}
      <ul className="mt-6 space-y-2">
        {(items as { product_name: string; quantity_on_hand: number; availability_status: string }[]).map(
          (i, idx) => (
            <li
              key={idx}
              className="rounded-lg border border-sovereign-800 px-4 py-3 text-sm"
            >
              <span className="font-medium">{i.product_name}</span>
              <span className="ml-2 text-slate-500">
                qty {i.quantity_on_hand} · {i.availability_status}
              </span>
            </li>
          )
        )}
      </ul>
    </div>
  );
}
