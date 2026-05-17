"use client";

import { useCallback, useEffect, useState } from "react";
import {
  clearTokens,
  fetchPermissions,
  fetchProfile,
  login as apiLogin,
  persistTokens,
  type LoginPayload,
} from "@/services/auth";
import { useAuthStore } from "@/store/auth-store";

export function useAuth() {
  const { user, permissions, isAuthenticated, setUser, setPermissions, logout: storeLogout } =
    useAuthStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const bootstrap = useCallback(async () => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nptte_access_token") : null;
    if (!token) {
      setLoading(false);
      return;
    }
    try {
      const profile = await fetchProfile();
      const perms = await fetchPermissions();
      setUser(profile);
      setPermissions(perms);
    } catch {
      clearTokens();
      storeLogout();
    } finally {
      setLoading(false);
    }
  }, [setUser, setPermissions, storeLogout]);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const login = async (payload: LoginPayload) => {
    setError(null);
    const tokens = await apiLogin(payload);
    persistTokens(tokens);
    const profile = await fetchProfile();
    const perms = await fetchPermissions();
    setUser(profile);
    setPermissions(perms);
  };

  const logout = () => {
    clearTokens();
    storeLogout();
  };

  return { user, permissions, isAuthenticated, loading, error, login, logout, setError };
}
