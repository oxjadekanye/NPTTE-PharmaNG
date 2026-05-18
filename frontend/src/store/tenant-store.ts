"use client";

import { create } from "zustand";
import { persist } from "zustand/middleware";

type TenantState = {
  activeOrganisationId: string | null;
  membershipIds: string[];
  setContext: (activeOrganisationId: string | null, membershipIds?: string[]) => void;
};

export const useTenantStore = create<TenantState>()(
  persist(
    (set) => ({
      activeOrganisationId: null,
      membershipIds: [],
      setContext: (activeOrganisationId, membershipIds = []) =>
        set({ activeOrganisationId, membershipIds }),
    }),
    { name: "nptte-tenant-context" }
  )
);
