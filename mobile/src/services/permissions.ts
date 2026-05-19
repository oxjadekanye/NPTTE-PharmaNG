import * as ImagePicker from "expo-image-picker";
import * as LocalAuthentication from "expo-local-authentication";
import * as Location from "expo-location";
import { Camera } from "expo-camera";
import * as Notifications from "expo-notifications";
import { PERMISSION_COPY } from "@/services/permission-messages";

export { PERMISSION_COPY, type PermissionKind } from "@/services/permission-messages";

export async function requestCameraPermission() {
  const { status } = await Camera.requestCameraPermissionsAsync();
  return {
    granted: status === "granted",
    copy: status === "granted" ? null : PERMISSION_COPY.camera.denied,
  };
}

export async function requestLocationPermission() {
  const { status } = await Location.requestForegroundPermissionsAsync();
  return {
    granted: status === "granted",
    copy: status === "granted" ? null : PERMISSION_COPY.location.denied,
  };
}

export async function requestNotificationPermission() {
  const { status } = await Notifications.requestPermissionsAsync();
  return {
    granted: status === "granted",
    copy: status === "granted" ? null : PERMISSION_COPY.notifications.denied,
  };
}

export async function requestBiometricPermission() {
  const compatible = await LocalAuthentication.hasHardwareAsync();
  const enrolled = await LocalAuthentication.isEnrolledAsync();
  const granted = compatible && enrolled;
  return {
    granted,
    copy: granted ? null : PERMISSION_COPY.biometric.denied,
  };
}

export async function requestMediaPermission() {
  const { status } = await ImagePicker.requestMediaLibraryPermissionsAsync();
  return {
    granted: status === "granted",
    copy: status === "granted" ? null : PERMISSION_COPY.media.denied,
  };
}
