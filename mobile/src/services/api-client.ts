import { resolveApiBaseUrl, API_TIMEOUT_MS } from "@/config/env";
import { getAccessToken } from "@/services/auth-storage";
import { CrashReporting } from "@/services/crash-reporting";
import { recordApiLatency } from "@/services/performance-monitor";
import {
  handleSessionExpiry,
  isSessionExpired,
  refreshAccessToken,
} from "@/services/session-security";
import { useOperationalToast } from "@/store/operational-toast-store";

let networkOnline = true;

export function setApiNetworkOnline(online: boolean) {
  networkOnline = online;
}

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

  if (!networkOnline && init.method && init.method !== "GET") {
    useOperationalToast.getState().show("Offline — request queued or deferred", "warning");
    return { success: false, message: "Device offline", data: undefined as T };
  }

  const started = Date.now();
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
  recordApiLatency(path, Date.now() - started, res.ok);

  if (!res.ok) {
    const message = json.message || json.detail || res.statusText;
    CrashReporting.capture("warning", `API ${path}: ${message}`, { status: res.status });
    if (res.status >= 500 || res.status === 429) {
      useOperationalToast.getState().show(message, "error");
    }
    return {
      success: false,
      message,
      data: json.data,
    };
  }
  if (typeof json.success === "boolean") {
    if (!json.success) {
      useOperationalToast.getState().show(json.message || "Request failed", "warning");
    }
    return json;
  }
  return { success: true, message: "OK", data: json as T };
}
