import {
  applyShellFromCache,
  hydrateAuthInBackground,
  resetAuthShellBootstrap,
} from "./auth-shell-bootstrap";

let bootstrapPromise: Promise<void> | null = null;

/** Deduped background auth refresh — never blocks shell render. */
export function ensureAuthBootstrap(): Promise<void> {
  if (bootstrapPromise) return bootstrapPromise;
  bootstrapPromise = new Promise((resolve) => {
    applyShellFromCache();
    hydrateAuthInBackground();
    resolve();
  });
  return bootstrapPromise;
}

export function resetAuthBootstrap() {
  bootstrapPromise = null;
  resetAuthShellBootstrap();
}
