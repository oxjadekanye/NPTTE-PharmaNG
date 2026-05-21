import { useRef } from "react";
import { useNavigationStore } from "@/store/navigation-store";

/** Prevent duplicate route pushes; defer until root layout is mounted. */
export function useSafeNavigation() {
  const lockRef = useRef(false);
  const replaceWhenReady = useNavigationStore((s) => s.replaceWhenReady);

  const safeReplace = (href: string) => {
    if (lockRef.current) return false;
    lockRef.current = true;
    replaceWhenReady(href);
    setTimeout(() => {
      lockRef.current = false;
    }, 1500);
    return true;
  };

  return { safeReplace, isLocked: () => lockRef.current };
}
