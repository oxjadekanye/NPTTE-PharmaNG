import * as Notifications from "expo-notifications";
import { Platform } from "react-native";
import { registerMobileDevice } from "@/services/mobile-device";
import { useOfflineQueue } from "@/store/offline-queue";

Notifications.setNotificationHandler({
  handleNotification: async () => ({
    shouldShowAlert: true,
    shouldPlaySound: false,
    shouldSetBadge: false,
  }),
});

/**
 * Phase 21 foundation — registers device for future push (recalls, tasks, suspicious scans).
 * Does not publish to app stores yet.
 */
export async function initPushFoundation() {
  const deviceId = useOfflineQueue.getState().ensureDeviceId();
  if (Platform.OS === "android") {
    await Notifications.setNotificationChannelAsync("default", {
      name: "NPTTE Alerts",
      importance: Notifications.AndroidImportance.DEFAULT,
    });
  }
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== "granted") {
    return { ok: false, reason: "permission_denied" };
  }
  try {
    await registerMobileDevice(deviceId);
  } catch {
    /* backend may require auth — caller should retry after login */
  }
  return { ok: true, deviceId };
}
