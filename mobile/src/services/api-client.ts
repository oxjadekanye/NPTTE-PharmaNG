import { API_BASE } from "@/config/api";
import { getAccessToken } from "@/services/auth-storage";

export type ApiEnvelope<T> = {
  success: boolean;
  message: string;
  data: T;
  meta?: Record<string, unknown>;
};

export async function apiRequest<T>(
  path: string,
  options: RequestInit & { auth?: boolean } = {}
): Promise<ApiEnvelope<T>> {
  const { auth = true, ...init } = options;
  const headers = new Headers(init.headers);
  headers.set("Content-Type", "application/json");
  if (auth) {
    const token = await getAccessToken();
    if (token) headers.set("Authorization", `Bearer ${token}`);
  }
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
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
