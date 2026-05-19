import Constants from "expo-constants";

export type AppEnvironment = "development" | "staging" | "production";

const extra = Constants.expoConfig?.extra ?? {};

export function resolveAppEnvironment(): AppEnvironment {
  const raw =
    process.env.EXPO_PUBLIC_APP_ENV ??
    (extra.appEnv as string | undefined) ??
    (__DEV__ ? "development" : "production");
  if (raw === "staging" || raw === "production" || raw === "development") return raw;
  return "development";
}

export const APP_ENV = resolveAppEnvironment();

export const IS_PRODUCTION = APP_ENV === "production";
export const IS_STAGING = APP_ENV === "staging";
export const IS_DEV = APP_ENV === "development";

const API_URLS: Record<AppEnvironment, string> = {
  development: "http://localhost:8000/api/v1",
  staging: "https://nptte-backend-staging.onrender.com/api/v1",
  production: "https://nptte-backend.onrender.com/api/v1",
};

export function resolveApiBaseUrl(): string {
  return (
    process.env.EXPO_PUBLIC_API_BASE_URL ??
    (extra.apiBaseUrl as string | undefined) ??
    API_URLS[APP_ENV]
  );
}

export const API_TIMEOUT_MS = Number(process.env.EXPO_PUBLIC_API_TIMEOUT_MS ?? 30_000);
