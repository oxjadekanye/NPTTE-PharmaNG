import { router } from "expo-router";
import { create } from "zustand";
import { bootLog } from "@/services/boot-diagnostics";

type NavigationState = {
  rootMounted: boolean;
  currentPath: string;
  pendingRoute: string | null;
  setRootMounted: () => void;
  setCurrentPath: (path: string) => void;
  replaceWhenReady: (href: string) => void;
  flushPending: () => void;
  clearNavigationDedupe: () => void;
};

function normalizePath(path: string) {
  const base = path.split("?")[0] || "/";
  if (base.length > 1 && base.endsWith("/")) return base.slice(0, -1);
  return base || "/";
}

function scheduleNavigation(fn: () => void) {
  if (typeof requestAnimationFrame === "function") {
    requestAnimationFrame(fn);
  } else {
    setTimeout(fn, 0);
  }
}

function runReplace(href: string) {
  try {
    router.replace(href as never);
    bootLog("navigation", `replace → ${href}`);
  } catch (err) {
    bootLog("navigation", `replace failed, trying push → ${href}`);
    try {
      router.push(href as never);
    } catch (pushErr) {
      bootLog(
        "navigation",
        `push failed ${pushErr instanceof Error ? pushErr.message : "unknown"}`
      );
      useNavigationStore.setState({ pendingRoute: href });
    }
  }
}

export const useNavigationStore = create<NavigationState>((set, get) => ({
  rootMounted: false,
  currentPath: "/",
  pendingRoute: null,
  setRootMounted: () => {
    if (get().rootMounted) {
      get().flushPending();
      return;
    }
    set({ rootMounted: true });
    bootLog("navigation", "root layout mounted — ready");
    get().flushPending();
  },
  setCurrentPath: (path) => set({ currentPath: normalizePath(path) }),
  clearNavigationDedupe: () => set({ pendingRoute: null }),
  replaceWhenReady: (href) => {
    const target = normalizePath(href);
    const state = get();
    if (state.currentPath === target) {
      bootLog("navigation", `already on ${target}`);
      return;
    }
    if (!state.rootMounted) {
      bootLog("navigation", `queued → ${target}`);
      set({ pendingRoute: target });
      return;
    }
    set({ pendingRoute: null });
    scheduleNavigation(() => runReplace(target));
  },
  flushPending: () => {
    const { pendingRoute, rootMounted, currentPath } = get();
    if (!rootMounted || !pendingRoute) return;
    const target = normalizePath(pendingRoute);
    if (currentPath === target) {
      set({ pendingRoute: null });
      return;
    }
    set({ pendingRoute: null });
    scheduleNavigation(() => runReplace(target));
  },
}));

export function isNavigationReady() {
  return useNavigationStore.getState().rootMounted;
}
