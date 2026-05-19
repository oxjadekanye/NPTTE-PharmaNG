import { resolveApiBaseUrl } from "@/config/env";

/** Resolved API base for current environment */
export const API_BASE = resolveApiBaseUrl();

export { APP_ENV, IS_PRODUCTION, IS_DEV, IS_STAGING, resolveApiBaseUrl } from "@/config/env";
