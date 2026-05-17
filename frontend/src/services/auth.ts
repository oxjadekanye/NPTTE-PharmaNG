import { API_BASE } from "./api-client";

export type LoginPayload = { username: string; password: string };
export type TokenPair = { access: string; refresh: string };
export type UserProfile = {
  id: string;
  username: string;
  email: string;
  role_code?: string;
  organisation?: string | null;
  organisation_id?: string | null;
};

async function authFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const headers = new Headers(init?.headers);
  headers.set("Content-Type", "application/json");
  const token =
    typeof window !== "undefined" ? localStorage.getItem("nptte_access_token") : null;
  if (token) headers.set("Authorization", `Bearer ${token}`);
  const res = await fetch(`${API_BASE}${path}`, { ...init, headers });
  const json = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error((json as { detail?: string }).detail ?? res.statusText);
  return json as T;
}

export async function login(payload: LoginPayload): Promise<TokenPair> {
  return authFetch<TokenPair>("/auth/login/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function fetchProfile(): Promise<UserProfile> {
  return authFetch<UserProfile>("/auth/profile/");
}

export async function fetchPermissions(): Promise<string[]> {
  const data = await authFetch<{ permissions: string[] }>("/auth/permissions/");
  return data.permissions ?? [];
}

export function persistTokens(tokens: TokenPair): void {
  localStorage.setItem("nptte_access_token", tokens.access);
  localStorage.setItem("nptte_refresh_token", tokens.refresh);
}

export function clearTokens(): void {
  localStorage.removeItem("nptte_access_token");
  localStorage.removeItem("nptte_refresh_token");
}
