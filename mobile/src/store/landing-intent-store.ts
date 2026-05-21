import { create } from "zustand";

/** When true, landing must not auto-redirect to role home (user chose citizen/public flow). */
type LandingIntentState = {
  bypassAutoRedirect: boolean;
  setBypassAutoRedirect: (value: boolean) => void;
};

export const useLandingIntent = create<LandingIntentState>((set) => ({
  bypassAutoRedirect: false,
  setBypassAutoRedirect: (value) => set({ bypassAutoRedirect: value }),
}));
