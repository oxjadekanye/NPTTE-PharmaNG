import { useState } from "react";
import {
  ActivityIndicator,
  Image,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as ImageManipulator from "expo-image-manipulator";
import * as Location from "expo-location";
import { uploadFieldEvidence, type EvidencePhoto } from "@/services/evidence";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";
import { PERMISSION_COPY, requestCameraPermission, requestMediaPermission } from "@/services/permissions";
import { useEvidenceQueue } from "@/store/evidence-queue";
import { useOfflineQueue } from "@/store/offline-queue";
import { useNetwork } from "@/hooks/useNetwork";

type Props = {
  evidenceType: string;
  serialNumber?: string;
};

export function EvidenceCapture({ evidenceType, serialNumber = "" }: Props) {
  const [notes, setNotes] = useState("");
  const [photos, setPhotos] = useState<EvidencePhoto[]>([]);
  const [status, setStatus] = useState<string | null>(null);
  const [statusKind, setStatusKind] = useState<"info" | "success" | "error">("info");
  const [capturing, setCapturing] = useState(false);
  const [uploading, setUploading] = useState(false);
  const { online } = useNetwork();
  const enqueue = useEvidenceQueue((s) => s.enqueue);
  const ensureDeviceId = useOfflineQueue((s) => s.ensureDeviceId);

  const setMessage = (message: string, kind: "info" | "success" | "error" = "info") => {
    setStatus(message);
    setStatusKind(kind);
  };

  const capturePhoto = async () => {
    mobileActionLog("capture_photo_pressed");
    if (capturing || uploading) return;
    setCapturing(true);
    setMessage("Opening camera…");
    try {
      const cam = await requestCameraPermission();
      const pickerCam = await ImagePicker.requestCameraPermissionsAsync();
      if (!cam.granted && !pickerCam.granted) {
        setMessage(cam.copy ?? PERMISSION_COPY.camera.denied, "error");
        return;
      }

      let shot = await ImagePicker.launchCameraAsync({
        mediaTypes: ImagePicker.MediaTypeOptions.Images,
        allowsEditing: false,
        quality: 0.6,
        base64: true,
      });

      if (shot.canceled) {
        const media = await requestMediaPermission();
        if (!media.granted) {
          setMessage("Photo capture cancelled", "info");
          return;
        }
        shot = await ImagePicker.launchImageLibraryAsync({
          mediaTypes: ImagePicker.MediaTypeOptions.Images,
          allowsEditing: false,
          quality: 0.6,
          base64: true,
        });
        if (shot.canceled) {
          setMessage("Photo capture cancelled", "info");
          return;
        }
      }

      const asset = shot.assets?.[0];
      if (!asset?.uri) {
        setMessage("No image captured. Try again or pick from gallery.", "error");
        return;
      }

      const manipulated = await ImageManipulator.manipulateAsync(
        asset.uri,
        [{ resize: { width: 1280 } }],
        { compress: 0.42, format: ImageManipulator.SaveFormat.JPEG, base64: true }
      );

      const base64 = manipulated.base64 ?? asset.base64 ?? "";
      if (!base64) {
        setMessage("Could not process image. Try a smaller photo.", "error");
        return;
      }

      setPhotos((p) => [
        ...p,
        {
          id: `ph-${Date.now()}`,
          mime: "image/jpeg",
          base64,
          uri: manipulated.uri ?? asset.uri,
          upload_status: "pending",
        },
      ]);
      setMessage("Photo captured — ready to upload", "success");
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Camera unavailable";
      setMessage(`Capture failed: ${msg}`, "error");
    } finally {
      setCapturing(false);
    }
  };

  const upload = async () => {
    if (uploading || capturing) return;
    if (photos.length === 0) {
      setMessage("Capture a photo before uploading", "error");
      return;
    }
    setUploading(true);
    setMessage("Uploading evidence…");
    try {
      let lat: number | undefined;
      let lng: number | undefined;
      try {
        const { status: locStatus } = await Location.requestForegroundPermissionsAsync();
        if (locStatus === "granted") {
          const loc = await Location.getCurrentPositionAsync({});
          lat = loc.coords.latitude;
          lng = loc.coords.longitude;
        }
      } catch {
        /* optional */
      }

      if (!online) {
        enqueue({ evidence_type: evidenceType, notes, serial_number: serialNumber, photos });
        setMessage("Queued offline — will sync when online", "success");
        return;
      }

      const res = await uploadFieldEvidence({
        device_id: ensureDeviceId(),
        evidence_type: evidenceType,
        notes,
        serial_number: serialNumber,
        latitude: lat,
        longitude: lng,
        photos,
      });
      if (res.success) {
        setMessage("Evidence uploaded successfully", "success");
        setPhotos([]);
        setNotes("");
      } else {
        enqueue({ evidence_type: evidenceType, notes, serial_number: serialNumber, photos });
        setMessage(`Upload failed — queued for retry: ${res.message}`, "error");
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Upload failed";
      try {
        enqueue({ evidence_type: evidenceType, notes, serial_number: serialNumber, photos });
        setMessage(`Upload error — queued for retry: ${msg}`, "error");
      } catch {
        setMessage(`Upload error: ${msg}`, "error");
      }
    } finally {
      setUploading(false);
    }
  };

  const busy = capturing || uploading;

  return (
    <View style={styles.box}>
      <Text style={styles.label}>Evidence: {evidenceType}</Text>
      <TextInput
        style={styles.input}
        placeholder="Notes"
        placeholderTextColor="#64748b"
        value={notes}
        onChangeText={setNotes}
        multiline
        editable={!busy}
      />
      <Pressable
        style={[styles.btn, busy && styles.btnDisabled]}
        onPress={capturePhoto}
        disabled={busy}
        accessibilityRole="button"
        accessibilityLabel="Capture photo"
      >
        {capturing ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Capture photo</Text>
        )}
      </Pressable>
      {photos.length > 0 && (
        <Text style={styles.captured}>{photos.length} photo(s) captured</Text>
      )}
      {photos.map((p) => (
        <Image
          key={p.id}
          source={
            p.uri
              ? { uri: p.uri }
              : { uri: `data:${p.mime};base64,${p.base64}` }
          }
          style={styles.thumb}
        />
      ))}
      <Pressable
        style={[styles.btn, styles.upload, busy && styles.btnDisabled]}
        onPress={upload}
        disabled={busy}
        accessibilityRole="button"
        accessibilityLabel="Upload or queue evidence"
      >
        {uploading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Upload / queue evidence</Text>
        )}
      </Pressable>
      {status ? (
        <Text
          style={[
            styles.status,
            statusKind === "success" && styles.statusSuccess,
            statusKind === "error" && styles.statusError,
          ]}
        >
          {status}
        </Text>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  box: { gap: 8 },
  label: { color: "#94a3b8", fontSize: 12 },
  input: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    padding: 10,
    color: "#f1f5f9",
    minHeight: 60,
    backgroundColor: "#0f172a",
  },
  btn: {
    backgroundColor: "#334155",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
    minHeight: 44,
    justifyContent: "center",
  },
  upload: { backgroundColor: "#0284c7" },
  btnDisabled: { opacity: 0.55 },
  btnText: { color: "#fff" },
  captured: { color: "#86efac", fontSize: 12 },
  thumb: { width: "100%", height: 120, borderRadius: 8 },
  status: { color: "#94a3b8", fontSize: 12 },
  statusSuccess: { color: "#86efac" },
  statusError: { color: "#fca5a5" },
});
