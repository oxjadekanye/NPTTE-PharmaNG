import { CameraView, useCameraPermissions } from "expo-camera";
import { useCallback, useEffect, useRef, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { endTimer, startTimer } from "@/services/performance-monitor";
import { PERMISSION_COPY } from "@/services/permissions";
import { NPTTEBrand } from "@/theme/branding";

const DEBOUNCE_MS = 900;

type Props = {
  onScan: (value: string) => void;
  active?: boolean;
};

export function BarcodeScanner({ onScan, active = true }: Props) {
  const [permission, requestPermission] = useCameraPermissions();
  const [last, setLast] = useState("");
  const [torch, setTorch] = useState(false);
  const lastAtRef = useRef(0);
  const mountedRef = useRef(true);

  useEffect(() => {
    mountedRef.current = true;
    return () => {
      mountedRef.current = false;
    };
  }, []);

  const handleBarcode = useCallback(
    (data: string) => {
      if (!data || !mountedRef.current) return;
      const now = Date.now();
      if (data === last && now - lastAtRef.current < DEBOUNCE_MS) return;
      if (now - lastAtRef.current < DEBOUNCE_MS) return;
      lastAtRef.current = now;
      setLast(data);
      startTimer("scan.process");
      onScan(data);
      endTimer("scan", "scan.process", { codeLength: data.length });
    },
    [last, onScan]
  );

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
        <Pressable style={styles.btnSecondary} onPress={() => void requestPermission()}>
          <Text style={styles.btnText}>Try again</Text>
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
        enableTorch={torch}
        barcodeScannerSettings={{
          barcodeTypes: ["qr", "ean13", "ean8", "code128", "code39"],
        }}
        onBarcodeScanned={({ data }) => {
          if (data) handleBarcode(data);
        }}
      />
      <Pressable style={styles.torchBtn} onPress={() => setTorch((t) => !t)}>
        <Text style={styles.torchText}>{torch ? "Torch on" : "Torch off"}</Text>
      </Pressable>
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
  btnSecondary: {
    marginTop: 8,
    backgroundColor: "#334155",
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
  torchBtn: {
    position: "absolute",
    right: 8,
    bottom: 8,
    backgroundColor: "rgba(0,0,0,0.55)",
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6,
  },
  torchText: { color: "#fff", fontSize: 11, fontWeight: "600" },
});
