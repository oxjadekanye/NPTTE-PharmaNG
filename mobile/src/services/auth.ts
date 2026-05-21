import { resolveApiBaseUrl, API_TIMEOUT_MS } from "@/config/env";
import { apiRequest } from "@/services/api-client";
import { clearTokens, persistTokens, setTokenExpiry } from "@/services/auth-storage";
import { decodeJwtExpiry, secureLogout } from "@/services/session-security";

export type LoginPayload = { username: string; password: string };

export const LOGIN_VALIDATION_HINT =
  "Login failed. Check username/password or confirm demo user is seeded on Render.";

/** Normalize Django/JWT login error payloads for display. */
export function parseLoginError(json: unknown, status: number): string {
  if (json && typeof json === "object") {
    const body = json as Record<string, unknown>;
    const detail = body.detail;
    if (typeof detail === "string") {
      if (/no active account|inactive|disabled/i.test(detail)) {
        return LOGIN_VALIDATION_HINT;
      }
      return detail;
    }
    if (Array.isArray(detail)) {
      return detail
        .map((item) =>
          typeof item === "string" ? item : String((item as { msg?: string })?.msg ?? item)
        )
        .join(". ");
    }
    if (typeof body.message === "string") return body.message;
    const nonField = body.non_field_errors;
    if (Array.isArray(nonField) && nonField.length > 0) {
      return String(nonField[0]);
    }
  }
  if (status === 401 || status === 403) {
    return LOGIN_VALIDATION_HINT;
  }
  return LOGIN_VALIDATION_HINT;
}
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
  const controller = new AbortController();
  const timeout = setTimeout(() => controller.abort(), API_TIMEOUT_MS);
  try {
    const res = await fetch(`${resolveApiBaseUrl()}/auth/login/`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ username: payload.username, password: payload.password }),
      signal: controller.signal,
    });
    const json = await res.json().catch(() => ({}));
    if (!res.ok) {
      throw new Error(parseLoginError(json, res.status));
    }
    const access = (json as { access?: string }).access;
    const refresh = (json as { refresh?: string }).refresh;
    if (!access || !refresh) {
      throw new Error("Login response missing tokens");
    }
    await persistTokens(access, refresh);
    const exp = decodeJwtExpiry(access);
    if (exp) await setTokenExpiry(exp);
    return { access, refresh };
  } catch (err) {
    if (err instanceof Error && err.name === "AbortError") {
      throw new Error("Login timed out — check network and API URL.");
    }
    throw err;
  } finally {
    clearTimeout(timeout);
  }
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
  await secureLogout();
}
