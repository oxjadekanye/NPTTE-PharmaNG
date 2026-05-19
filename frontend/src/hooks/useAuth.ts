"use client";

import { useCallback, useEffect, useState } from "react";
import {
  clearTokens,
  fetchPermissions,
  fetchProfile,
  login as apiLogin,
  persistTokens,
  type LoginPayload,
  type UserProfile,
} from "@/services/auth";
import { clearAuthSession, readAuthSession, writeAuthSession } from "@/services/auth-session-cache";
import { clearFastSession, readFastSession, writeFastSession } from "@/services/auth-fast-session";
import { ensureAuthBootstrap, resetAuthBootstrap } from "@/services/auth-bootstrap";
import { useAuthStore } from "@/store/auth-store";
import { useTenantStore } from "@/store/tenant-store";

function stubUser(username: string): UserProfile {
  return {
    id: "pending",
    username,
    email: "",
    role_code: readFastSession()?.roleCode,
  };
}

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
    const fast = readFastSession();
    const cached = readAuthSession();
    if (fast || cached) {
      if (cached) {
        setUser(cached.user);
        setPermissions(cached.permissions);
        useTenantStore.getState().setContext(
          cached.organisationId,
          cached.membershipOrganisationIds
        );
      } else if (fast) {
        setUser(stubUser(fast.username));
        setPermissions(fast.permissions.length ? fast.permissions : ["regulatory.read"]);
      }
      setLoading(false);
    }
    try {
      await ensureAuthBootstrap();
    } catch {
      clearTokens();
      clearAuthSession();
      clearFastSession();
      storeLogout();
    } finally {
      setLoading(false);
    }
  }, [setUser, setPermissions, storeLogout]);

  useEffect(() => {
    void bootstrap();
  }, [bootstrap]);

  const login = async (payload: LoginPayload) => {
    setError(null);
    resetAuthBootstrap();
    const tokens = await apiLogin(payload);
    persistTokens(tokens);
    setUser(stubUser(payload.username));
    setPermissions(["regulatory.read"]);
    const [profile, permsPayload] = await Promise.all([fetchProfile(), fetchPermissions()]);
    setUser(profile);
    setPermissions(permsPayload.permissions ?? []);
    writeAuthSession(profile, permsPayload);
    writeFastSession(profile, permsPayload);
    useTenantStore.getState().setContext(
      permsPayload.organisation_id ? String(permsPayload.organisation_id) : null,
      (permsPayload.membership_organisation_ids ?? []).map(String)
    );
  };

  const logout = () => {
    clearTokens();
    clearAuthSession();
    clearFastSession();
    resetAuthBootstrap();
    storeLogout();
  };

  return { user, permissions, isAuthenticated, loading, error, login, logout, setError };
}
