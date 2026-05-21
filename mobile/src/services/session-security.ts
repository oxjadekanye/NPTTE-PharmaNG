import { API_BASE } from "@/config/api";
import { useNavigationStore } from "@/store/navigation-store";
import { API_TIMEOUT_MS } from "@/config/env";
import {
  clearTokens,
  getAccessToken,
  getRefreshToken,
  getTokenExpiry,
  persistTokens,
  setTokenExpiry,
} from "@/services/auth-storage";
import { useOfflineQueue } from "@/store/offline-queue";
import { useEvidenceQueue } from "@/store/evidence-queue";

let refreshInFlight: Promise<boolean> | null = null;

/** Decode JWT exp claim (seconds) — best-effort. */
export function decodeJwtExpiry(token: string): number | null {
  try {
    const payload = token.split(".")[1];
    if (!payload) return null;
    const json = JSON.parse(atob(payload.replace(/-/g, "+").replace(/_/g, "/"))) as { exp?: number };
    return json.exp ? json.exp * 1000 : null;
  } catch {
    return null;
  }
}

export async function isSessionExpired(): Promise<boolean> {
  const exp = await getTokenExpiry();
  if (!exp) return false;
  return Date.now() >= exp - 30_000;
}

export async function refreshAccessToken(): Promise<boolean> {
  if (refreshInFlight) return refreshInFlight;
  refreshInFlight = (async () => {
    const refresh = await getRefreshToken();
    if (!refresh) return false;
    const controller = new AbortController();
    const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
    try {
      const res = await fetch(`${API_BASE}/auth/refresh/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
        signal: controller.signal,
      });
      const json = await res.json().catch(() => ({}));
      if (!res.ok) return false;
      const access = json.access as string | undefined;
      const newRefresh = (json.refresh as string | undefined) ?? refresh;
      if (!access) return false;
      await persistTokens(access, newRefresh);
      const exp = decodeJwtExpiry(access);
      if (exp) await setTokenExpiry(exp);
      return true;
    } catch {
      return false;
    } finally {
      clearTimeout(timeout);
      refreshInFlight = null;
    }
  })();
  return refreshInFlight;
}

export async function secureLogout(): Promise<void> {
  const refresh = await getRefreshToken();
  try {
    if (refresh) {
      await fetch(`${API_BASE}/auth/logout/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ refresh }),
      });
    }
  } catch {
    /* best effort */
  }
  await clearTokens();
  useOfflineQueue.setState({ queue: [], deviceId: "", lastSyncAt: null });
  useEvidenceQueue.setState({ queue: [], lastSyncAt: null });
}

let sessionExpiryHandling = false;

export async function handleSessionExpiry(): Promise<void> {
  if (sessionExpiryHandling) return;
  sessionExpiryHandling = true;
  try {
    await secureLogout();
    useNavigationStore.getState().clearNavigationDedupe();
    useNavigationStore.getState().replaceWhenReady("/login");
  } finally {
    sessionExpiryHandling = false;
  }
}

/** Placeholder — integrate expo-screen-capture when enabling sensitive screens. */
export const ScreenProtection = {
  enable: async () => {
    /* no-op until native module wired */
  },
  disable: async () => {
    /* no-op */
  },
};
