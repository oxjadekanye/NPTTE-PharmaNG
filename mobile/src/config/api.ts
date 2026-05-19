import Constants from "expo-constants";

/** Override via app.json extra.apiBaseUrl or EXPO_PUBLIC_API_BASE_URL */
export const API_BASE =
  process.env.EXPO_PUBLIC_API_BASE_URL ??
  (Constants.expoConfig?.extra?.apiBaseUrl as string | undefined) ??
  "http://localhost:8000/api/v1";
