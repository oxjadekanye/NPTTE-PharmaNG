import * as Application from "expo-application";
import * as Device from "expo-device";
import { Platform } from "react-native";
import { apiRequest } from "@/services/api-client";
import { useOfflineQueue } from "@/store/offline-queue";

export type DeviceTrustState = {
  device_id: string;
  trusted_status: string;
  device_risk_level: string;
  trust_score: number;
  suspicious_device: boolean;
  offline_sync_token?: string;
};

/** Build a stable device fingerprint (no secrets). */
export async function buildDeviceFingerprint(): Promise<string> {
  const parts = [
    Device.modelName ?? "unknown",
    Device.osName ?? Platform.OS,
    Device.osVersion ?? "",
    Application.applicationId ?? "",
    Platform.OS === "ios"
      ? String(await Application.getIosIdForVendorAsync().catch(() => ""))
      : String(Application.getAndroidId() ?? ""),
  ];
  return parts.join("|");
}

/** Placeholder root/jailbreak detection — extend with native module in production. */
export function detectDeviceRiskFlags() {
  const isEmulator = !Device.isDevice;
  const isRooted = false; // placeholder — integrate jail-monkey or similar
  const suspicious = isEmulator;
  return { isEmulator, isRooted, suspicious };
}

export async function registerTrustedDevice(biometricCapable: boolean) {
  const deviceId = useOfflineQueue.getState().ensureDeviceId();
  const fingerprint = await buildDeviceFingerprint();
  const flags = detectDeviceRiskFlags();
  return apiRequest<DeviceTrustState>("/mobile/devices/trust/", {
    method: "POST",
    body: JSON.stringify({
      device_id: deviceId,
      fingerprint,
      platform: Platform.OS,
      app_version: Application.nativeApplicationVersion ?? "0.1.0",
      os_version: Device.osVersion ?? "",
      is_emulator: flags.isEmulator,
      is_rooted: flags.isRooted,
      suspicious: flags.suspicious,
      biometric_capable: biometricCapable,
    }),
  });
}

export async function sendDeviceHeartbeat(rotateSession = false) {
  const deviceId = useOfflineQueue.getState().deviceId;
  if (!deviceId) return null;
  return apiRequest<Record<string, unknown>>("/mobile/devices/heartbeat/", {
    method: "POST",
    body: JSON.stringify({
      device_id: deviceId,
      app_version: Application.nativeApplicationVersion ?? "0.1.0",
      rotate_session: rotateSession,
    }),
  });
}
