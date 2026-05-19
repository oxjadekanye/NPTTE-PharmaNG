"use client";

import { useCallback, useEffect, useState } from "react";
import { clearTokens, login as apiLogin, persistTokens, type LoginPayload } from "@/services/auth";
import { clearAuthSession } from "@/services/auth-session-cache";
import { clearFastSession, writeFastSession } from "@/services/auth-fast-session";
import {
  applyShellFromCache,
  hydrateAuthInBackground,
  onAuthHydrationFailed,
  resetAuthShellBootstrap,
} from "@/services/auth-shell-bootstrap";
import { resetAuthBootstrap } from "@/services/auth-bootstrap";
import { useAuthStore } from "@/store/auth-store";

export function useAuth() {
  const { user, permissions, isAuthenticated, setUser, setPermissions, logout: storeLogout } =
    useAuthStore();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const bootstrap = useCallback(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nptte_access_token") : null;
    if (!token) {
      setLoading(false);
      return;
    }
    applyShellFromCache();
    setLoading(false);
    hydrateAuthInBackground();
  }, []);

  useEffect(() => {
    bootstrap();
  }, [bootstrap]);

  /** Token only — navigate immediately; profile hydrates in background. */
  const login = async (payload: LoginPayload): Promise<void> => {
    setError(null);
    resetAuthBootstrap();
    resetAuthShellBootstrap();
    const tokens = await apiLogin(payload);
    persistTokens(tokens);
    applyShellFromCache();
    writeFastSession(
      { id: "shell", username: payload.username, email: "", role_code: "regulator" },
      { permissions: ["regulatory.read"], role_code: "regulator", is_regulator: true }
    );
    hydrateAuthInBackground(true);
  };

  const logout = () => {
    clearTokens();
    clearAuthSession();
    clearFastSession();
    resetAuthBootstrap();
    resetAuthShellBootstrap();
    storeLogout();
  };

  return { user, permissions, isAuthenticated, loading, error, login, logout, setError };
}
