import { useState } from "react";
import { Image, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import * as ImagePicker from "expo-image-picker";
import * as ImageManipulator from "expo-image-manipulator";
import * as Location from "expo-location";
import { uploadFieldEvidence, type EvidencePhoto } from "@/services/evidence";
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
  const { online } = useNetwork();
  const enqueue = useEvidenceQueue((s) => s.enqueue);
  const ensureDeviceId = useOfflineQueue((s) => s.ensureDeviceId);

  const capturePhoto = async () => {
    const perm = await ImagePicker.requestCameraPermissionsAsync();
    if (!perm.granted) {
      setStatus("Camera permission required");
      return;
    }
    const shot = await ImagePicker.launchCameraAsync({ quality: 0.6, base64: true });
    if (shot.canceled || !shot.assets[0]?.base64) return;
    const manipulated = await ImageManipulator.manipulateAsync(
      shot.assets[0].uri,
      [{ resize: { width: 1024 } }],
      { compress: 0.5, format: ImageManipulator.SaveFormat.JPEG, base64: true }
    );
    setPhotos((p) => [
      ...p,
      {
        id: `ph-${Date.now()}`,
        mime: "image/jpeg",
        base64: manipulated.base64 ?? shot.assets[0].base64 ?? "",
        upload_status: "pending",
      },
    ]);
  };

  const upload = async () => {
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
      setStatus("Queued offline — will sync when online");
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
    setStatus(res.success ? "Evidence uploaded" : res.message);
  };

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
      />
      <Pressable style={styles.btn} onPress={() => void capturePhoto()}>
        <Text style={styles.btnText}>Capture photo</Text>
      </Pressable>
      {photos.map((p) => (
        <Image
          key={p.id}
          source={{ uri: `data:${p.mime};base64,${p.base64}` }}
          style={styles.thumb}
        />
      ))}
      <Pressable style={[styles.btn, styles.upload]} onPress={() => void upload()}>
        <Text style={styles.btnText}>Upload / queue evidence</Text>
      </Pressable>
      {status && <Text style={styles.status}>{status}</Text>}
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
  },
  upload: { backgroundColor: "#0284c7" },
  btnText: { color: "#fff" },
  thumb: { width: "100%", height: 120, borderRadius: 8 },
  status: { color: "#86efac", fontSize: 12 },
});
