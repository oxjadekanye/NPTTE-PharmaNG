import AsyncStorage from "@react-native-async-storage/async-storage";
import { create } from "zustand";
import { createJSONStorage, persist } from "zustand/middleware";

type QaModeState = {
  enabled: boolean;
  unlock: () => void;
  disable: () => void;
};

export const useQaMode = create<QaModeState>()(
  persist(
    (set) => ({
      enabled: __DEV__,
      unlock: () => set({ enabled: true }),
      disable: () => set({ enabled: false }),
    }),
    { name: "nptte-qa-mode", storage: createJSONStorage(() => AsyncStorage) }
  )
);
