"use client";

import { useEffect, useState } from "react";
import { OnboardingStatusBanner } from "@/components/tenant/OnboardingStatusBanner";
import { fetchOrganisationSettings } from "@/services/operations";
import { useTenantStore } from "@/store/tenant-store";

export function OperationalBanners() {
  const activeOrgId = useTenantStore((s) => s.activeOrganisationId);
  const [settings, setSettings] = useState<Record<string, unknown> | null>(null);

  useEffect(() => {
    if (!activeOrgId) return;
    fetchOrganisationSettings(activeOrgId)
      .then((res) => setSettings(res.data ?? null))
      .catch(() => setSettings(null));
  }, [activeOrgId]);

  const openTasks = Number(settings?.open_tasks ?? 0);
  const readiness = settings?.operational_readiness as string | undefined;

  return (
    <div className="space-y-2 px-6 pt-4 lg:px-8">
      <OnboardingStatusBanner />
      {openTasks > 0 && (
        <div className="rounded-lg border border-amber-500/30 bg-amber-500/10 px-4 py-2 text-xs text-amber-200">
          {openTasks} operational task{openTasks > 1 ? "s" : ""} pending — review your task queue.
        </div>
      )}
      {readiness === "pending" && (
        <div className="rounded-lg border border-sky-500/30 bg-sky-500/10 px-4 py-2 text-xs text-sky-200">
          Operational readiness pending — upload compliance documents to complete your profile.
        </div>
      )}
    </div>
  );
}
