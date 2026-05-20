/** Phase 24 hotfix — safe startup diagnostics (dev-visible). */
export function bootLog(stage: string, detail?: string) {
  const suffix = detail ? ` — ${detail}` : "";
  if (__DEV__) {
    // eslint-disable-next-line no-console
    console.log(`[BOOT] ${stage}${suffix}`);
  }
}

export const BOOT_HARD_TIMEOUT_MS = 4000;
