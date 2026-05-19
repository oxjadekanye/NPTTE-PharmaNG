"use client";

import { useCallback, useEffect, useState } from "react";
import { clearTokens, fetchPermissions, fetchProfile, login as apiLogin, persistTokens, type LoginPayload } from "@/services/auth";
import { ensureAuthBootstrap, resetAuthBootstrap } from "@/services/auth-bootstrap";
import { useAuthStore } from "@/store/auth-store";
import { useTenantStore } from "@/store/tenant-store";

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
      await ensureAuthBootstrap();
    } catch {
      clearTokens();
      storeLogout();
    } finally {
      setLoading(false);
    }
  }, [storeLogout]);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  const login = async (payload: LoginPayload) => {
    setError(null);
    resetAuthBootstrap();
    const tokens = await apiLogin(payload);
    persistTokens(tokens);
    const [profile, permsPayload] = await Promise.all([fetchProfile(), fetchPermissions()]);
    setUser(profile);
    setPermissions(permsPayload.permissions ?? []);
    useTenantStore.getState().setContext(
      permsPayload.organisation_id ? String(permsPayload.organisation_id) : null,
      (permsPayload.membership_organisation_ids ?? []).map(String)
    );
  };

  const logout = () => {
    clearTokens();
    resetAuthBootstrap();
    storeLogout();
  };

  return { user, permissions, isAuthenticated, loading, error, login, logout, setError };
}
