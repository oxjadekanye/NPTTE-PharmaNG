import AsyncStorage from "@react-native-async-storage/async-storage";
import * as Notifications from "expo-notifications";
import { registerTrustedDevice } from "@/services/device-trust";

const PREFS_KEY = "nptte_push_prefs";

export type PushPreferences = {
  recalls: boolean;
  enforcement: boolean;
  suspicious_scans: boolean;
  regional: boolean;
  task_deadlines: boolean;
  executive_critical: boolean;
};

const DEFAULT_PREFS: PushPreferences = {
  recalls: true,
  enforcement: true,
  suspicious_scans: true,
  regional: true,
  task_deadlines: true,
  executive_critical: true,
};

export async function loadPushPreferences(): Promise<PushPreferences> {
  const raw = await AsyncStorage.getItem(PREFS_KEY);
  if (!raw) return DEFAULT_PREFS;
  return { ...DEFAULT_PREFS, ...JSON.parse(raw) };
}

export async function savePushPreferences(prefs: PushPreferences) {
  await AsyncStorage.setItem(PREFS_KEY, JSON.stringify(prefs));
}

/** Register device + notification channels for role-based alerts (foundation). */
export async function initPushOrchestration(roleChannel: string) {
  const { status } = await Notifications.requestPermissionsAsync();
  if (status !== "granted") return { ok: false };
  await registerTrustedDevice(false);
  await Notifications.setNotificationChannelAsync("recalls", {
    name: "Recall alerts",
    importance: Notifications.AndroidImportance.HIGH,
  });
  await Notifications.setNotificationChannelAsync("tasks", {
    name: "Task deadlines",
    importance: Notifications.AndroidImportance.DEFAULT,
  });
  await Notifications.setNotificationChannelAsync(roleChannel, {
    name: "Operational feed",
    importance: Notifications.AndroidImportance.DEFAULT,
  });
  return { ok: true };
}

export async function showLocalOperationalAlert(title: string, body: string) {
  await Notifications.scheduleNotificationAsync({
    content: { title, body, sound: true },
    trigger: null,
  });
}
