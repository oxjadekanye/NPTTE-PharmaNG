/** Phase 24 hotfix — safe startup diagnostics (dev-visible). */
export function bootLog(stage: string, detail?: string) {
  const suffix = detail ? ` — ${detail}` : "";
  if (typeof __DEV__ !== "undefined" ? __DEV__ : process.env.NODE_ENV !== "production") {
    // eslint-disable-next-line no-console
    console.log(`[BOOT] ${stage}${suffix}`);
  }
}

export const BOOT_HARD_TIMEOUT_MS = 4000;
