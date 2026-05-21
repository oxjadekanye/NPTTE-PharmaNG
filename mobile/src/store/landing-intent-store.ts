import { create } from "zustand";

type LandingIntentState = {
  bypassAutoRedirect: boolean;
  preferLanding: boolean;
  /** User tapped Staff Login — must show /login even if already authenticated. */
  staffLoginIntent: boolean;
  setBypassAutoRedirect: (value: boolean) => void;
  setPreferLanding: (value: boolean) => void;
  setStaffLoginIntent: (value: boolean) => void;
  clearPublicFlow: () => void;
};

export const useLandingIntent = create<LandingIntentState>((set) => ({
  bypassAutoRedirect: false,
  preferLanding: false,
  staffLoginIntent: false,
  setBypassAutoRedirect: (value) => set({ bypassAutoRedirect: value }),
  setPreferLanding: (value) => set({ preferLanding: value }),
  setStaffLoginIntent: (value) => set({ staffLoginIntent: value }),
  clearPublicFlow: () =>
    set({ bypassAutoRedirect: false, preferLanding: false, staffLoginIntent: false }),
}));
