import { CameraView, useCameraPermissions } from "expo-camera";
import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { PERMISSION_COPY } from "@/services/permissions";
import { NPTTEBrand } from "@/theme/branding";

type Props = {
  onScan: (value: string) => void;
  active?: boolean;
};

export function BarcodeScanner({ onScan, active = true }: Props) {
  const [permission, requestPermission] = useCameraPermissions();
  const [last, setLast] = useState("");

  if (!permission) {
    return <Text style={styles.muted}>Checking camera permission…</Text>;
  }

  if (!permission.granted) {
    return (
      <View style={styles.box}>
        <Text style={styles.muted}>{PERMISSION_COPY.camera.denied}</Text>
        <Text style={styles.rationale}>{PERMISSION_COPY.camera.rationale}</Text>
        <Pressable style={styles.btn} onPress={() => void requestPermission()}>
          <Text style={styles.btnText}>Grant permission</Text>
        </Pressable>
      </View>
    );
  }

  if (!active) return null;

  return (
    <View style={styles.wrap}>
      <CameraView
        style={styles.camera}
        facing="back"
        barcodeScannerSettings={{
          barcodeTypes: ["qr", "ean13", "ean8", "code128", "code39"],
        }}
        onBarcodeScanned={({ data }) => {
          if (!data || data === last) return;
          setLast(data);
          onScan(data);
        }}
      />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { height: 220, borderRadius: 12, overflow: "hidden", marginVertical: 12 },
  camera: { flex: 1 },
  box: { padding: 16, backgroundColor: "#111827", borderRadius: 12 },
  muted: { color: "#94a3b8", fontSize: 13 },
  btn: {
    marginTop: 12,
    backgroundColor: "#0ea5e9",
    padding: 10,
    borderRadius: 8,
    alignItems: "center",
  },
  btnText: { color: "#fff", fontWeight: "600" },
  rationale: {
    color: NPTTEBrand.colors.sovereign.muted,
    fontSize: 11,
    marginTop: 8,
    lineHeight: 16,
  },
});
