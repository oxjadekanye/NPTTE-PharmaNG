import type { ExpoConfig, ConfigContext } from "expo/config";

const APP_ENV = process.env.APP_ENV ?? process.env.EXPO_PUBLIC_APP_ENV ?? "development";

const apiByEnv: Record<string, string> = {
  development: "http://localhost:8000/api/v1",
  staging: "https://nptte-backend-staging.onrender.com/api/v1",
  production: "https://nptte-backend.onrender.com/api/v1",
};

export default ({ config }: ConfigContext): ExpoConfig => ({
  ...config,
  name: "NPTTE PharmaNG",
  slug: "nptte-pharmang",
  version: "1.0.0",
  orientation: "portrait",
  scheme: "nptte",
  userInterfaceStyle: "dark",
  newArchEnabled: true,
  icon: "./assets/branding/icon.png",
  splash: {
    image: "./assets/branding/splash-logo.png",
    resizeMode: "contain",
    backgroundColor: "#020617",
  },
  ios: {
    supportsTablet: true,
    bundleIdentifier: "ng.gov.nptte.mobile",
    buildNumber: "1",
    infoPlist: {
      NSCameraUsageDescription:
        "NPTTE requires camera access to scan pharmaceutical serial numbers, QR codes, and capture field evidence for national traceability operations.",
      NSLocationWhenInUseUsageDescription:
        "NPTTE uses your location only while scanning or capturing evidence to anchor field operations to verified geographic coordinates for enforcement records.",
      NSPhotoLibraryUsageDescription:
        "NPTTE may access photos when attaching field evidence to inspection or enforcement cases.",
      NSFaceIDUsageDescription:
        "NPTTE uses Face ID for secure biometric unlock of regulator and field officer sessions.",
      UIBackgroundModes: ["fetch", "remote-notification"],
    },
  },
  android: {
    adaptiveIcon: {
      foregroundImage: "./assets/branding/adaptive-icon-foreground.png",
      backgroundColor: "#020617",
    },
    package: "ng.gov.nptte.mobile",
    versionCode: 1,
    permissions: [
      "CAMERA",
      "ACCESS_NETWORK_STATE",
      "INTERNET",
      "ACCESS_COARSE_LOCATION",
      "ACCESS_FINE_LOCATION",
      "VIBRATE",
      "USE_BIOMETRIC",
      "USE_FINGERPRINT",
    ],
  },
  plugins: [
    "expo-router",
    [
      "expo-camera",
      {
        cameraPermission:
          "NPTTE requires camera access to scan pharmaceutical serial numbers and capture field evidence.",
      },
    ],
    [
      "expo-notifications",
      {
        icon: "./assets/branding/notification-icon.png",
        color: "#38bdf8",
      },
    ],
    "expo-asset",
    "expo-secure-store",
  ],
  experiments: { typedRoutes: true },
  extra: {
    appEnv: APP_ENV,
    apiBaseUrl: process.env.EXPO_PUBLIC_API_BASE_URL ?? apiByEnv[APP_ENV] ?? apiByEnv.development,
    eas: {
      projectId: process.env.EAS_PROJECT_ID ?? "REPLACE_WITH_EAS_PROJECT_ID",
    },
  },
  owner: process.env.EXPO_OWNER,
});
