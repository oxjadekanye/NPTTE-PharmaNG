/**
 * Shell-first auth: show UI immediately, hydrate profile/permissions in background.
 */
import { clearTokens, fetchPermissions, fetchProfile } from "./auth";
import { clearAuthSession, readAuthSession, writeAuthSession } from "./auth-session-cache";
import { clearFastSession, readFastSession, writeFastSession } from "./auth-fast-session";
import { enqueueHydration, HydrationPriority } from "./hydration-queue";
import { useAuthStore } from "@/store/auth-store";
import { useTenantStore } from "@/store/tenant-store";

let hydrateStarted = false;

export function applyShellFromCache(): boolean {
  const token = typeof window !== "undefined" ? localStorage.getItem("nptte_access_token") : null;
  if (!token) return false;

  const cached = readAuthSession();
  const fast = readFastSession();
  const { setUser, setPermissions } = useAuthStore.getState();

  if (cached) {
    setUser(cached.user);
    setPermissions(cached.permissions);
    useTenantStore.getState().setContext(cached.organisationId, cached.membershipOrganisationIds);
    return true;
  }
  if (fast) {
    setUser({
      id: "shell",
      username: fast.username,
      email: "",
      role_code: fast.roleCode,
    });
    setPermissions(fast.permissions.length ? fast.permissions : ["regulatory.read"]);
    return true;
  }
  setUser({ id: "shell", username: "Commander", email: "", role_code: "regulator" });
  setPermissions(["regulatory.read"]);
  return true;
}

export function hydrateAuthInBackground(force = false): void {
  if (hydrateStarted && !force) return;
  const token = typeof window !== "undefined" ? localStorage.getItem("nptte_access_token") : null;
  if (!token) return;
  hydrateStarted = true;

  enqueueHydration(
    "auth:profile-permissions",
    async (_signal) => {
      try {
        const [profile, permsPayload] = await Promise.all([fetchProfile(), fetchPermissions()]);
        const { setUser, setPermissions } = useAuthStore.getState();
        setUser(profile);
        setPermissions(permsPayload.permissions ?? []);
        writeAuthSession(profile, permsPayload);
        writeFastSession(profile, permsPayload);
        useTenantStore.getState().setContext(
          permsPayload.organisation_id ? String(permsPayload.organisation_id) : null,
          (permsPayload.membership_organisation_ids ?? []).map(String)
        );
      } catch {
        onAuthHydrationFailed();
      }
    },
    HydrationPriority.SHELL
  );
}

export function onAuthHydrationFailed(): void {
  hydrateStarted = false;
  clearTokens();
  clearAuthSession();
  clearFastSession();
  useAuthStore.getState().logout();
}

export function resetAuthShellBootstrap(): void {
  hydrateStarted = false;
}
