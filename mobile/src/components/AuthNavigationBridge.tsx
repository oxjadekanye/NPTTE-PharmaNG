import { usePathname } from "expo-router";
import { useEffect, useRef } from "react";
import { useRootMounted } from "@/hooks/useRootMounted";
import { bootLog } from "@/services/boot-diagnostics";
import { mobileHomePath } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";

/** Only auto-redirect authenticated users from landing — not from /login. */
const LANDING_AUTO_REDIRECT = new Set(["/", "", "/index"]);

function isCitizenRoute(pathname: string) {
  return pathname === "/citizen" || pathname.startsWith("/citizen/");
}

function normalizePath(pathname: string) {
  return pathname.replace(/\/$/, "") || "/";
}

/**
 * Single post-auth navigation authority — login and landing must not each call router.replace.
 */
export function AuthNavigationBridge() {
  const pathname = usePathname() || "/";
  const rootMounted = useRootMounted();
  const mobileRole = useAuthStore((s) => s.mobileRole);
  const loading = useAuthStore((s) => s.loading);
  const bypassAutoRedirect = useLandingIntent((s) => s.bypassAutoRedirect);
  const preferLanding = useLandingIntent((s) => s.preferLanding);
  const staffLoginIntent = useLandingIntent((s) => s.staffLoginIntent);
  const setStaffLoginIntent = useLandingIntent((s) => s.setStaffLoginIntent);
  const setCurrentPath = useNavigationStore((s) => s.setCurrentPath);
  const replaceWhenReady = useNavigationStore((s) => s.replaceWhenReady);
  const lastHandled = useRef<string | null>(null);

  useEffect(() => {
    setCurrentPath(pathname);
  }, [pathname, setCurrentPath]);

  useEffect(() => {
    if (!rootMounted || loading) return;

    const normalizedPath = normalizePath(pathname);

    if (isCitizenRoute(normalizedPath)) {
      bootLog("navigation", "skip — citizen public route");
      return;
    }

    if (normalizedPath === "/login") {
      if (staffLoginIntent) {
        bootLog("navigation", "stay on login — staff login intent");
        lastHandled.current = null;
        return;
      }
      if (mobileRole) {
        const target = mobileHomePath(mobileRole);
        const key = `login-complete:${target}`;
        if (lastHandled.current !== key) {
          lastHandled.current = key;
          bootLog("navigation", `login screen → ${target}`);
          useNavigationStore.getState().clearNavigationDedupe();
          replaceWhenReady(target);
        }
      }
      return;
    }

    if (!mobileRole) return;

    if (preferLanding && LANDING_AUTO_REDIRECT.has(normalizedPath)) {
      bootLog("navigation", "skip — user chose landing");
      lastHandled.current = null;
      return;
    }

    if (bypassAutoRedirect && LANDING_AUTO_REDIRECT.has(normalizedPath)) {
      bootLog("navigation", "skip — citizen/public landing intent");
      return;
    }

    if (!LANDING_AUTO_REDIRECT.has(normalizedPath)) {
      lastHandled.current = null;
      return;
    }

    const target = mobileHomePath(mobileRole);
    const key = `${mobileRole}:${target}`;
    if (lastHandled.current === key) return;
    lastHandled.current = key;

    bootLog("navigation", `post-auth → ${target} (from ${pathname})`);
    useNavigationStore.getState().clearNavigationDedupe();
    replaceWhenReady(target);
  }, [
    rootMounted,
    loading,
    mobileRole,
    pathname,
    bypassAutoRedirect,
    preferLanding,
    staffLoginIntent,
    replaceWhenReady,
  ]);

  return null;
}
