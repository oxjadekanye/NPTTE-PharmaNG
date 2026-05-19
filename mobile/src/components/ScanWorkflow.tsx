import { useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import { BarcodeScanner } from "@/components/BarcodeScanner";
import { useScanSubmit } from "@/hooks/useScanSubmit";
import type { ScanType } from "@/services/scanning";

type Props = {
  title: string;
  scanType: ScanType;
  actorRole: string;
};

export function ScanWorkflow({ title, scanType, actorRole }: Props) {
  const [serial, setSerial] = useState("");
  const [cameraOn, setCameraOn] = useState(false);
  const { submit, loading, result, error, clear } = useScanSubmit(scanType, actorRole);

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      <Pressable style={styles.toggle} onPress={() => setCameraOn((v) => !v)}>
        <Text style={styles.toggleText}>{cameraOn ? "Hide camera" : "Scan QR / barcode"}</Text>
      </Pressable>
      {cameraOn && (
        <BarcodeScanner
          active={cameraOn}
          onScan={(v) => {
            setSerial(v);
            void submit(v);
          }}
        />
      )}
      <TextInput
        style={styles.input}
        placeholder="Or enter serial manually"
        placeholderTextColor="#64748b"
        value={serial}
        onChangeText={setSerial}
        autoCapitalize="characters"
      />
      <Pressable
        style={styles.btn}
        disabled={loading}
        onPress={() => void submit(serial)}
      >
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Submit scan</Text>}
      </Pressable>
      {error && <Text style={styles.error}>{error}</Text>}
      {result && (
        <View style={styles.result}>
          <Text style={styles.resultTitle}>Outcome: {result.outcome_label}</Text>
          <Text style={styles.muted}>Risk {result.risk_score}</Text>
          {result.alerts?.counterfeit_warning && (
            <Text style={styles.warn}>Counterfeit warning</Text>
          )}
          {result.alerts?.recall_alert && <Text style={styles.warn}>Recall alert</Text>}
          <Pressable onPress={clear}>
            <Text style={styles.link}>Clear</Text>
          </Pressable>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: 8 },
  title: { fontSize: 18, fontWeight: "600", color: "#f8fafc" },
  toggle: { paddingVertical: 8 },
  toggleText: { color: "#38bdf8", fontSize: 14 },
  input: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    padding: 12,
    color: "#f1f5f9",
    backgroundColor: "#0f172a",
  },
  btn: {
    backgroundColor: "#0284c7",
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  btnText: { color: "#fff", fontWeight: "600" },
  error: { color: "#fca5a5", fontSize: 13 },
  result: {
    marginTop: 12,
    padding: 12,
    backgroundColor: "#1e293b",
    borderRadius: 8,
    gap: 4,
  },
  resultTitle: { color: "#f8fafc", fontWeight: "600" },
  muted: { color: "#94a3b8", fontSize: 12 },
  warn: { color: "#fbbf24", fontSize: 12 },
  link: { color: "#38bdf8", marginTop: 8 },
});
