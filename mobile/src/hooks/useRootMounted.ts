import { useNavigationStore } from "@/store/navigation-store";

/** True after root layout Stack has mounted and pending routes may flush. */
export function useRootMounted() {
  return useNavigationStore((s) => s.rootMounted);
}
