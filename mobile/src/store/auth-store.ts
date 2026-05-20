import { create } from "zustand";
import type { PermissionsPayload, UserProfile } from "@/services/auth";
import { fetchPermissions, fetchProfile, logout as apiLogout } from "@/services/auth";
import { getAccessToken } from "@/services/auth-storage";
import { isSessionExpired, refreshAccessToken } from "@/services/session-security";
import { bootLog, BOOT_HARD_TIMEOUT_MS } from "@/services/boot-diagnostics";
import { mobileHomePath, resolveMobileRole, type MobileRole } from "@/services/role-routing";

type AuthState = {
  loading: boolean;
  profile: UserProfile | null;
  permissions: PermissionsPayload | null;
  mobileRole: MobileRole | null;
  sessionExpired: boolean;
  hydrate: () => Promise<MobileRole | null>;
  signOut: () => Promise<void>;
};

let hydrateInFlight: Promise<MobileRole | null> | null = null;

function withBootTimeout<T>(promise: Promise<T>, fallback: T): Promise<T> {
  return Promise.race([
    promise,
    new Promise<T>((resolve) => {
      setTimeout(() => resolve(fallback), BOOT_HARD_TIMEOUT_MS);
    }),
  ]);
}

export const useAuthStore = create<AuthState>((set, get) => ({
  loading: true,
  profile: null,
  permissions: null,
  mobileRole: null,
  sessionExpired: false,
  hydrate: async () => {
    if (hydrateInFlight) {
      bootLog("auth hydrate", "reusing in-flight promise");
      return hydrateInFlight;
    }

    const coldStart = !get().profile && get().mobileRole == null;
    hydrateInFlight = (async () => {
      bootLog("auth hydrate", "start");
      if (coldStart) set({ loading: true, sessionExpired: false });

      try {
        const role = await withBootTimeout(runHydrateBody(set), null);
        if (role === null && coldStart) {
          bootLog("auth hydrate", "timeout or no session — landing ready");
        }
        return role;
      } catch (err) {
        bootLog("auth hydrate", `error ${err instanceof Error ? err.message : "unknown"}`);
        set({ profile: null, permissions: null, mobileRole: null, loading: false });
        return null;
      } finally {
        set({ loading: false });
        hydrateInFlight = null;
        bootLog("auth hydrate", "done");
      }
    })();

    return hydrateInFlight;
  },
  signOut: async () => {
    await apiLogout();
    set({ profile: null, permissions: null, mobileRole: null, sessionExpired: false, loading: false });
  },
}));

async function runHydrateBody(
  set: (partial: Partial<AuthState>) => void
): Promise<MobileRole | null> {
  const token = await getAccessToken();
  if (!token) {
    set({ profile: null, permissions: null, mobileRole: null, loading: false });
    bootLog("auth hydrate", "no token");
    return null;
  }

  if (await isSessionExpired()) {
    bootLog("auth hydrate", "refreshing session");
    const ok = await refreshAccessToken();
    if (!ok) {
      await apiLogout();
      set({
        profile: null,
        permissions: null,
        mobileRole: null,
        loading: false,
        sessionExpired: true,
      });
      bootLog("auth hydrate", "session expired");
      return null;
    }
  }

  const [profile, permissions] = await Promise.all([fetchProfile(), fetchPermissions()]);
  const role = resolveMobileRole(permissions.role_code, permissions.is_regulator);
  set({ profile, permissions, mobileRole: role, loading: false });
  bootLog("auth hydrate", role ? `role=${role}` : "no mobile role");
  return role;
}

export function homeHrefForStore(): string {
  const role = useAuthStore.getState().mobileRole;
  return role ? mobileHomePath(role) : "/login";
}
