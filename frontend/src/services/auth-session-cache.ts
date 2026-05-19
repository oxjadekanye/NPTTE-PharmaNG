import type { PermissionsPayload } from "./auth";
import type { UserProfile } from "./auth";

const SESSION_KEY = "nptte_auth_session_v1";
const TTL_MS = 5 * 60 * 1000;

type AuthSession = {
  ts: number;
  user: UserProfile;
  permissions: string[];
  organisationId: string | null;
  membershipOrganisationIds: string[];
};

export function readAuthSession(): AuthSession | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(SESSION_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as AuthSession;
    if (Date.now() - parsed.ts > TTL_MS) return null;
    return parsed;
  } catch {
    return null;
  }
}

export function writeAuthSession(
  user: UserProfile,
  perms: PermissionsPayload
): void {
  if (typeof window === "undefined") return;
  const entry: AuthSession = {
    ts: Date.now(),
    user,
    permissions: perms.permissions ?? [],
    organisationId: perms.organisation_id ? String(perms.organisation_id) : null,
    membershipOrganisationIds: (perms.membership_organisation_ids ?? []).map(String),
  };
  try {
    sessionStorage.setItem(SESSION_KEY, JSON.stringify(entry));
  } catch {
    /* ignore */
  }
}

export function clearAuthSession(): void {
  if (typeof window === "undefined") return;
  sessionStorage.removeItem(SESSION_KEY);
}

const STAFF_KEY = "nptte_explorer_staff_v1";
const STAFF_TTL = 10 * 60 * 1000;

export function readStaffCache():
  | { id: string; full_name: string; role_title?: string; team?: string }[]
  | null {
  if (typeof window === "undefined") return null;
  try {
    const raw = sessionStorage.getItem(STAFF_KEY);
    if (!raw) return null;
    const parsed = JSON.parse(raw) as { ts: number; staff: { id: string; full_name: string }[] };
    if (Date.now() - parsed.ts > STAFF_TTL) return null;
    return parsed.staff;
  } catch {
    return null;
  }
}

export function writeStaffCache(
  staff: { id: string; full_name: string; role_title?: string; team?: string }[]
): void {
  if (typeof window === "undefined") return;
  try {
    sessionStorage.setItem(STAFF_KEY, JSON.stringify({ ts: Date.now(), staff }));
  } catch {
    /* ignore */
  }
}
