import { usePathname } from "expo-router";
import { useEffect, useRef } from "react";
import { useRootMounted } from "@/hooks/useRootMounted";
import { bootLog } from "@/services/boot-diagnostics";
import { mobileHomePath } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";

const ENTRY_ROUTES = new Set(["/", "", "/login", "/index"]);

function isCitizenRoute(pathname: string) {
  return pathname === "/citizen" || pathname.startsWith("/citizen/");
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
  const setCurrentPath = useNavigationStore((s) => s.setCurrentPath);
  const replaceWhenReady = useNavigationStore((s) => s.replaceWhenReady);
  const lastHandled = useRef<string | null>(null);

  useEffect(() => {
    setCurrentPath(pathname);
  }, [pathname, setCurrentPath]);

  useEffect(() => {
    if (!rootMounted || loading || !mobileRole) return;

    if (isCitizenRoute(pathname)) {
      bootLog("navigation", "skip — citizen public route");
      return;
    }

    if (preferLanding && (pathname === "/" || pathname === "")) {
      bootLog("navigation", "skip — user chose landing");
      lastHandled.current = null;
      return;
    }

    if (bypassAutoRedirect && (pathname === "/" || pathname === "")) {
      bootLog("navigation", "skip — citizen/public landing intent");
      return;
    }

    const normalizedPath = pathname.replace(/\/$/, "") || "/";
    if (!ENTRY_ROUTES.has(normalizedPath)) {
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
    replaceWhenReady,
  ]);

  return null;
}
