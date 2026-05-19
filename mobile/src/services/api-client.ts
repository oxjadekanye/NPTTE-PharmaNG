import { resolveApiBaseUrl, API_TIMEOUT_MS } from "@/config/env";
import { getAccessToken } from "@/services/auth-storage";
import {
  handleSessionExpiry,
  isSessionExpired,
  refreshAccessToken,
} from "@/services/session-security";

export type ApiEnvelope<T> = {
  success: boolean;
  message: string;
  data: T;
  meta?: Record<string, unknown>;
};

async function fetchWithTimeout(url: string, init: RequestInit) {
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  try {
    return await fetch(url, { ...init, signal: controller.signal });
  } finally {
    clearTimeout(timeout);
  }
}

export async function apiRequest<T>(
  path: string,
  options: RequestInit & { auth?: boolean; skipRefresh?: boolean } = {}
): Promise<ApiEnvelope<T>> {
  const { auth = true, skipRefresh = false, ...init } = options;
  const base = resolveApiBaseUrl();

  if (auth && !skipRefresh && (await isSessionExpired())) {
    const refreshed = await refreshAccessToken();
    if (!refreshed) {
      await handleSessionExpiry();
      return { success: false, message: "Session expired", data: undefined as T };
    }
  }

  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (auth) {
    const token = await getAccessToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }

  let res = await fetchWithTimeout(`${base}${path}`, { ...init, headers });
  if (auth && res.status === 401 && !skipRefresh) {
    const refreshed = await refreshAccessToken();
    if (refreshed) {
      const token = await getAccessToken();
      if (token) headers.set("Authorization", `Bearer ${token}`);
      res = await fetchWithTimeout(`${base}${path}`, { ...init, headers });
    } else {
      await handleSessionExpiry();
      return { success: false, message: "Session expired", data: undefined as T };
    }
  }

  const json = (await res.json().catch(() => ({}))) as ApiEnvelope<T> & { detail?: string };
  if (!res.ok) {
    return {
      success: false,
      message: json.message || json.detail || res.statusText,
      data: json.data,
    };
  }
  if (typeof json.success === "boolean") return json;
  return { success: true, message: "OK", data: json as T };
}
