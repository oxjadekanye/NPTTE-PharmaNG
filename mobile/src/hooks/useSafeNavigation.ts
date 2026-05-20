import { router } from "expo-router";
import { useRef } from "react";

/** Prevent duplicate route pushes during login / hydration races. */
export function useSafeNavigation() {
  const lockRef = useRef(false);

  const safeReplace = (href: string) => {
    if (lockRef.current) return false;
    lockRef.current = true;
    router.replace(href as never);
    setTimeout(() => {
      lockRef.current = false;
    }, 1500);
    return true;
  };

  return { safeReplace, isLocked: () => lockRef.current };
}
