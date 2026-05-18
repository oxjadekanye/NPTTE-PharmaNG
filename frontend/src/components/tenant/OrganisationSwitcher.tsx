"use client";

import { useAuth } from "@/hooks/useAuth";
import { useTenantStore } from "@/store/tenant-store";
import { switchOrganisationContext } from "@/services/tenancy";

export function OrganisationSwitcher() {
  const { permissions } = useAuth();
  const activeId = useTenantStore((s) => s.activeOrganisationId);
  const membershipIds = useTenantStore((s) => s.membershipIds);
  const setContext = useTenantStore((s) => s.setContext);

  const isRegulator = permissions.includes("regulatory.read") || permissions.includes("regulatory.all");
  const options = membershipIds.length ? membershipIds : activeId ? [activeId] : [];

  if (!isRegulator && options.length <= 1) return null;

  async function onSwitch(orgId: string) {
    if (isRegulator) {
      await switchOrganisationContext(orgId);
    }
    setContext(orgId, membershipIds);
  }

  return (
    <div className="flex items-center gap-2 text-xs">
      <span className="text-slate-500">Organisation</span>
      <select
        className="rounded border border-sovereign-700 bg-sovereign-950 px-2 py-1 text-slate-200"
        value={activeId ?? ""}
        onChange={(e) => onSwitch(e.target.value)}
      >
        <option value="">National view</option>
        {options.map((id) => (
          <option key={id} value={id}>
            {id.slice(0, 8)}…
          </option>
        ))}
      </select>
    </div>
  );
}
