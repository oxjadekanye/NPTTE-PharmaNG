import { API_BASE } from "@/config/api";
import { apiRequest } from "@/services/api-client";
import { clearTokens, persistTokens } from "@/services/auth-storage";

export type LoginPayload = { username: string; password: string };
export type UserProfile = {
  id: string;
  username: string;
  email?: string;
  role_code?: string;
  organisation?: string | null;
  organisation_id?: string | null;
};

export type PermissionsPayload = {
  permissions: string[];
  role_code?: string;
  is_regulator?: boolean;
  organisation_id?: string | null;
};

export async function login(payload: LoginPayload) {
  const res = await fetch(`${API_BASE}/auth/login/`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) {
    throw new Error(json.detail || json.message || "Login failed");
  }
  await persistTokens(json.access, json.refresh);
  return json as { access: string; refresh: string };
}

export async function fetchProfile(): Promise<UserProfile> {
  const res = await apiRequest<UserProfile>("/auth/profile/");
  if (!res.success || !res.data) throw new Error(res.message);
  return res.data;
}

export async function fetchPermissions(): Promise<PermissionsPayload> {
  const res = await apiRequest<PermissionsPayload>("/auth/permissions/");
  if (!res.success || !res.data) throw new Error(res.message);
  return res.data;
}

export async function logout() {
  await clearTokens();
}
