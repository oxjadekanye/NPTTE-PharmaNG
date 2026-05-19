import { apiRequest } from "@/services/api-client";
import Constants from "expo-constants";
import { Platform } from "react-native";

/** Phase 21 — device registration placeholder for push + offline sync. */
export async function registerMobileDevice(deviceId: string) {
  return apiRequest<{
    device_id: string;
    offline_sync_token?: string;
  }>("/mobile/devices/register/", {
    method: "POST",
    body: JSON.stringify({
      device_id: deviceId,
      device_type: Platform.OS,
      app_version: Constants.expoConfig?.version ?? "0.1.0",
    }),
  });
}
