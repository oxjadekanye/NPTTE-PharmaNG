import { create } from "zustand";
import type { PermissionsPayload, UserProfile } from "@/services/auth";
import { fetchPermissions, fetchProfile, logout as apiLogout } from "@/services/auth";
import { getAccessToken } from "@/services/auth-storage";
import { isSessionExpired, refreshAccessToken } from "@/services/session-security";
import { mobileHomePath, resolveMobileRole, type MobileRole } from "@/lib/role-routing";

type AuthState = {
  loading: boolean;
  profile: UserProfile | null;
  permissions: PermissionsPayload | null;
  mobileRole: MobileRole | null;
  sessionExpired: boolean;
  hydrate: () => Promise<MobileRole | null>;
  signOut: () => Promise<void>;
};

export const useAuthStore = create<AuthState>((set) => ({
  loading: true,
  profile: null,
  permissions: null,
  mobileRole: null,
  sessionExpired: false,
  hydrate: async () => {
    set({ loading: true, sessionExpired: false });
    try {
      const token = await getAccessToken();
      if (!token) {
        set({ profile: null, permissions: null, mobileRole: null, loading: false });
        return null;
      }
      if (await isSessionExpired()) {
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
          return null;
        }
      }
      const [profile, permissions] = await Promise.all([fetchProfile(), fetchPermissions()]);
      const role = resolveMobileRole(permissions.role_code, permissions.is_regulator);
      set({ profile, permissions, mobileRole: role, loading: false });
      return role;
    } catch {
      set({ profile: null, permissions: null, mobileRole: null, loading: false });
      return null;
    }
  },
  signOut: async () => {
    await apiLogout();
    set({ profile: null, permissions: null, mobileRole: null, sessionExpired: false });
  },
}));

export function homeHrefForStore(): string {
  const role = useAuthStore.getState().mobileRole;
  return role ? mobileHomePath(role) : "/login";
}
