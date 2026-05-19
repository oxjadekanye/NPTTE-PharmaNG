export type PermissionKind = "camera" | "location" | "notifications" | "biometric" | "media";

export const PERMISSION_COPY: Record<
  PermissionKind,
  { title: string; rationale: string; denied: string }
> = {
  camera: {
    title: "Camera access",
    rationale:
      "NPTTE needs the camera to scan pharmaceutical serial numbers, QR codes, and capture field evidence for national traceability.",
    denied: "Camera access is required for scanning. Enable it in device Settings → NPTTE PharmaNG.",
  },
  location: {
    title: "Location access",
    rationale:
      "Location is used only when you scan or capture evidence to anchor field operations to verified coordinates for enforcement records.",
    denied: "Location helps anchor scan events. You may continue without GPS, but field records will lack coordinates.",
  },
  notifications: {
    title: "Notifications",
    rationale:
      "Operational alerts include recall notices, suspicious scan escalations, and task deadlines for field officers.",
    denied: "Notifications are disabled. You can still use the app; alerts will not appear on this device.",
  },
  biometric: {
    title: "Biometric unlock",
    rationale: "Use Face ID or fingerprint to protect regulator and field officer sessions on this device.",
    denied: "Biometric unlock unavailable. Use your password to sign in.",
  },
  media: {
    title: "Photo library",
    rationale: "Attach existing photos as field evidence for inspections and enforcement cases.",
    denied: "Photo access denied. Use the camera to capture new evidence instead.",
  },
};
