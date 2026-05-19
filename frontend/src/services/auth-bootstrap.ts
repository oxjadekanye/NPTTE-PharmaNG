import { clearTokens, fetchPermissions, fetchProfile } from "./auth";
import { useAuthStore } from "@/store/auth-store";
import { useTenantStore } from "@/store/tenant-store";

let bootstrapPromise: Promise<void> | null = null;

export function ensureAuthBootstrap(): Promise<void> {
  if (bootstrapPromise) return bootstrapPromise;
  bootstrapPromise = (async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nptte_access_token") : null;
    if (!token) return;
    const { setUser, setPermissions, logout } = useAuthStore.getState();
    try {
      const [profile, permsPayload] = await Promise.all([fetchProfile(), fetchPermissions()]);
      setUser(profile);
      setPermissions(permsPayload.permissions ?? []);
      useTenantStore.getState().setContext(
        permsPayload.organisation_id ? String(permsPayload.organisation_id) : null,
        (permsPayload.membership_organisation_ids ?? []).map(String)
      );
    } catch {
      clearTokens();
      logout();
      bootstrapPromise = null;
    }
  })();
  return bootstrapPromise;
}

export function resetAuthBootstrap() {
  bootstrapPromise = null;
}
