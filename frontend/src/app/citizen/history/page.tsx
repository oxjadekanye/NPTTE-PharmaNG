"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { apiRequest } from "@/services/api-client";

export default function CitizenHistoryPage() {
  const [history, setHistory] = useState<unknown[]>([]);

  useEffect(() => {
    apiRequest<{ history: unknown[] }>("/public/verification-history/", { auth: false }).then((r) => {
      if (r.success) setHistory(r.data?.history ?? []);
    });
  }, []);

  return (
    <div className="min-h-screen bg-sovereign-950 px-4 py-8 text-white">
      <Link href="/citizen" className="text-sm text-sky-400 hover:underline">
        ← Citizen portal
      </Link>
      <h1 className="mt-4 text-2xl font-bold">Verification history</h1>
      <ul className="mt-6 space-y-3">
        {(history as {
          serial_number: string;
          outcome: string;
          confidence_score: number;
          verified_at: string;
        }[]).map((h) => (
          <li key={String(h.verified_at) + h.serial_number} className="rounded-xl border border-sovereign-800 p-4">
            <p className="font-mono text-sm">{h.serial_number}</p>
            <p className="mt-1 text-xs text-slate-400">
              {h.outcome} · confidence {h.confidence_score}%
            </p>
          </li>
        ))}
      </ul>
    </div>
  );
}
