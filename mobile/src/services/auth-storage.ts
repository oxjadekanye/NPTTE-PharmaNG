import * as SecureStore from "expo-secure-store";

const ACCESS_KEY = "nptte_access_token";
const REFRESH_KEY = "nptte_refresh_token";
const EXPIRY_KEY = "nptte_token_expiry";

export async function getAccessToken(): Promise<string | null> {
  return SecureStore.getItemAsync(ACCESS_KEY);
}

export async function getRefreshToken(): Promise<string | null> {
  return SecureStore.getItemAsync(REFRESH_KEY);
}

export async function getTokenExpiry(): Promise<number | null> {
  const raw = await SecureStore.getItemAsync(EXPIRY_KEY);
  return raw ? Number(raw) : null;
}

export async function setTokenExpiry(expMs: number): Promise<void> {
  await SecureStore.setItemAsync(EXPIRY_KEY, String(expMs));
}

export async function persistTokens(access: string, refresh: string): Promise<void> {
  await SecureStore.setItemAsync(ACCESS_KEY, access);
  await SecureStore.setItemAsync(REFRESH_KEY, refresh);
}

export async function clearTokens(): Promise<void> {
  await SecureStore.deleteItemAsync(ACCESS_KEY);
  await SecureStore.deleteItemAsync(REFRESH_KEY);
  await SecureStore.deleteItemAsync(EXPIRY_KEY);
}
