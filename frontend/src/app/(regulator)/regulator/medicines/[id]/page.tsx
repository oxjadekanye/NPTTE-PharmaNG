"use client";

import { useEffect, useState } from "react";
import { useParams } from "next/navigation";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalSkeleton } from "@/components/ui/OperationalSkeleton";
import { fetchMedicineDetail } from "@/services/medicine-intelligence";

export default function MedicineDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [profile, setProfile] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!id) return;
    fetchMedicineDetail(id).then((r) => {
      if (r.success) setProfile(r.data ?? null);
    });
  }, [id]);

  return (
    <RegulatorGuard>
      <CommandShell title="Medicine profile" subtitle={String(profile?.name ?? id)}>
        {!profile ? (
          <OperationalSkeleton rows={6} />
        ) : (
          <div className="space-y-3 text-sm text-slate-300">
            <p>Risk: {String(profile.risk_classification)}</p>
            <p>Counterfeit vulnerability: {String(profile.counterfeit_vulnerability_score)}</p>
            <p>Shortage sensitivity: {String(profile.shortage_sensitivity_score)}</p>
            <p>Cold-chain: {profile.cold_chain_sensitive ? "Yes" : "No"}</p>
            <p className="text-xs text-slate-500">{String(profile.disclaimer)}</p>
          </div>
        )}
      </CommandShell>
    </RegulatorGuard>
  );
}
