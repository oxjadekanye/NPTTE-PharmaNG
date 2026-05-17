import { create } from "zustand";
import type { UserProfile } from "@/services/auth";

type AuthState = {
  user: UserProfile | null;
  permissions: string[];
  isAuthenticated: boolean;
  setUser: (user: UserProfile | null) => void;
  setPermissions: (permissions: string[]) => void;
  logout: () => void;
};

export const useAuthStore = create<AuthState>((set) => ({
  user: null,
  permissions: [],
  isAuthenticated: false,
  setUser: (user) => set({ user, isAuthenticated: !!user }),
  setPermissions: (permissions) => set({ permissions }),
  logout: () => set({ user: null, permissions: [], isAuthenticated: false }),
}));

export function hasPermission(permissions: string[], required: string): boolean {
  if (permissions.includes("admin.all")) return true;
  return permissions.some(
    (p) => p === required || p.endsWith(".all") || p.startsWith(required.split(".")[0])
  );
}
