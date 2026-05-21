import { create } from "zustand";

type LandingIntentState = {
  /** User chose citizen/public flow from landing — do not auto-redirect to role home. */
  bypassAutoRedirect: boolean;
  /** User explicitly returned to landing — stay on index even if authenticated. */
  preferLanding: boolean;
  setBypassAutoRedirect: (value: boolean) => void;
  setPreferLanding: (value: boolean) => void;
  clearPublicFlow: () => void;
};

export const useLandingIntent = create<LandingIntentState>((set) => ({
  bypassAutoRedirect: false,
  preferLanding: false,
  setBypassAutoRedirect: (value) => set({ bypassAutoRedirect: value }),
  setPreferLanding: (value) => set({ preferLanding: value }),
  clearPublicFlow: () => set({ bypassAutoRedirect: false, preferLanding: false }),
}));
