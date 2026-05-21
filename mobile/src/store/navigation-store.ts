import { router } from "expo-router";
import { create } from "zustand";
import { bootLog } from "@/services/boot-diagnostics";

type NavigationState = {
  rootMounted: boolean;
  pendingRoute: string | null;
  lastRoute: string | null;
  setRootMounted: () => void;
  replaceWhenReady: (href: string) => void;
  flushPending: () => void;
  resetLastRoute: () => void;
};

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
    bootLog("navigation", `replace failed ${err instanceof Error ? err.message : "unknown"}`);
    useNavigationStore.setState({ pendingRoute: href });
  }
}

export const useNavigationStore = create<NavigationState>((set, get) => ({
  rootMounted: false,
  pendingRoute: null,
  lastRoute: null,
  setRootMounted: () => {
    if (get().rootMounted) {
      get().flushPending();
      return;
    }
    set({ rootMounted: true });
    bootLog("navigation", "root layout mounted — ready");
    get().flushPending();
  },
  replaceWhenReady: (href) => {
    const state = get();
    if (state.lastRoute === href) {
      bootLog("navigation", `skip duplicate → ${href}`);
      return;
    }
    if (!state.rootMounted) {
      bootLog("navigation", `queued → ${href}`);
      set({ pendingRoute: href });
      return;
    }
    set({ lastRoute: href, pendingRoute: null });
    scheduleNavigation(() => runReplace(href));
  },
  flushPending: () => {
    const { pendingRoute, rootMounted, lastRoute } = get();
    if (!rootMounted || !pendingRoute || pendingRoute === lastRoute) return;
    set({ lastRoute: pendingRoute, pendingRoute: null });
    scheduleNavigation(() => runReplace(pendingRoute));
  },
  resetLastRoute: () => set({ lastRoute: null }),
}));

export function isNavigationReady() {
  return useNavigationStore.getState().rootMounted;
}
