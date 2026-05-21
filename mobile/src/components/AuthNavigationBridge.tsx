import { usePathname } from "expo-router";
import { useEffect, useRef } from "react";
import { useRootMounted } from "@/hooks/useRootMounted";
import { bootLog } from "@/services/boot-diagnostics";
import { mobileHomePath } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";

const ENTRY_ROUTES = new Set(["/", "", "/login", "/index"]);

/**
 * Single post-auth navigation authority — login and landing must not each call router.replace.
 */
export function AuthNavigationBridge() {
  const pathname = usePathname() || "/";
  const rootMounted = useRootMounted();
  const mobileRole = useAuthStore((s) => s.mobileRole);
  const loading = useAuthStore((s) => s.loading);
  const bypassAutoRedirect = useLandingIntent((s) => s.bypassAutoRedirect);
  const setCurrentPath = useNavigationStore((s) => s.setCurrentPath);
  const replaceWhenReady = useNavigationStore((s) => s.replaceWhenReady);
  const lastHandled = useRef<string | null>(null);

  useEffect(() => {
    setCurrentPath(pathname);
  }, [pathname, setCurrentPath]);

  useEffect(() => {
    if (!rootMounted || loading || !mobileRole) return;
    if (bypassAutoRedirect && (pathname === "/" || pathname === "")) {
      bootLog("navigation", "skip — citizen/public landing intent");
      return;
    }

    const target = mobileHomePath(mobileRole);
    const normalizedPath = pathname.replace(/\/$/, "") || "/";
    const normalizedTarget = target.replace(/\/$/, "");

    if (!ENTRY_ROUTES.has(normalizedPath)) {
      lastHandled.current = null;
      return;
    }

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
    replaceWhenReady,
  ]);

  return null;
}
