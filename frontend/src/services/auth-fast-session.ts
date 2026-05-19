import type { PermissionsPayload } from "./auth";
import type { UserProfile } from "./auth";

const FAST_KEY = "nptte_fast_session_v1";
const TTL_MS = 8 * 60 * 60 * 1000;

export type FastSession = {
  ts: number;
  username: string;
  roleCode: string;
  organisationId: string | null;
  permissions: string[];
  isRegulator: boolean;
};

export function readFastSession(): FastSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = localStorage.getItem(FAST_KEY);
    if (!raw) return null;
    const s = JSON.parse(raw) as FastSession;
    if (Date.now() - s.ts > TTL_MS) return null;
    if (!localStorage.getItem("nptte_access_token")) return null;
    return s;
  } catch {
    return null;
  }
}

export function writeFastSession(profile: UserProfile, perms: PermissionsPayload): void {
  if (typeof window === "undefined") return;
  const entry: FastSession = {
    ts: Date.now(),
    username: profile.username,
    roleCode: profile.role_code ?? perms.role_code ?? "",
    organisationId: profile.organisation_id
      ? String(profile.organisation_id)
      : perms.organisation_id
        ? String(perms.organisation_id)
        : null,
    permissions: perms.permissions ?? [],
    isRegulator: Boolean(perms.is_regulator),
  };
  try {
    localStorage.setItem(FAST_KEY, JSON.stringify(entry));
  } catch {
    /* ignore */
  }
}

export function clearFastSession(): void {
  if (typeof window === "undefined") return;
  localStorage.removeItem(FAST_KEY);
}
