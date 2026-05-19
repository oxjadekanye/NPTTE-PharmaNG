import { useCallback, useRef, useState } from "react";
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  TextInput,
  View,
} from "react-native";
import * as Haptics from "expo-haptics";
import { BarcodeScanner } from "@/components/BarcodeScanner";
import { useScanSubmit } from "@/hooks/useScanSubmit";
import { mobileCopilot } from "@/services/mobile-ai";
import type { ScanType } from "@/services/scanning";

type ScanMode = "standard" | "rapid" | "inspection" | "customs";

type Props = {
  title: string;
  scanType: ScanType;
  actorRole: string;
  mode?: ScanMode;
};

export function AdvancedScanWorkflow({ title, scanType, actorRole, mode = "standard" }: Props) {
  const [serial, setSerial] = useState("");
  const [cameraOn, setCameraOn] = useState(mode === "rapid");
  const [continuous, setContinuous] = useState(mode === "rapid");
  const [aiText, setAiText] = useState<string | null>(null);
  const lastScanRef = useRef("");
  const { submit, loading, result, error, clear } = useScanSubmit(scanType, actorRole);

  const handleScan = useCallback(
    async (value: string) => {
      const trimmed = value.trim();
      if (!trimmed || trimmed === lastScanRef.current) return;
      lastScanRef.current = trimmed;
      setSerial(trimmed);
      await Haptics.notificationAsync(Haptics.NotificationFeedbackType.Success);
      await submit(trimmed);
      if (!continuous) setCameraOn(false);
    },
    [submit, continuous]
  );

  const confidence =
    result?.risk_score != null
      ? result.risk_score > 70
        ? "high"
        : result.risk_score > 40
          ? "medium"
          : "low"
      : null;

  const askAi = async () => {
    const res = await mobileCopilot({
      prompt_mode: "explain_risk",
      serial_number: serial,
      user_question: `Explain counterfeit risk for field scan ${serial}`,
    });
    if (res.success && res.data) {
      setAiText(`${res.data.summary}\n\n${res.data.reasoning}`);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.hint}>
        {mode === "rapid" ? "Rapid mode — continuous scan" : "Align code inside frame · low-light supported"}
      </Text>
      <View style={styles.overlayBox}>
        {cameraOn && <BarcodeScanner active onScan={(v) => void handleScan(v)} />}
        <View style={styles.overlayFrame} pointerEvents="none" />
      </View>
      <View style={styles.row}>
        <Pressable onPress={() => setCameraOn((v) => !v)}>
          <Text style={styles.link}>{cameraOn ? "Hide camera" : "Open scanner"}</Text>
        </Pressable>
        <Pressable onPress={() => setContinuous((v) => !v)}>
          <Text style={styles.link}>{continuous ? "Continuous on" : "Continuous off"}</Text>
        </Pressable>
      </View>
      <TextInput
        style={styles.input}
        placeholder="Manual serial fallback"
        placeholderTextColor="#64748b"
        value={serial}
        onChangeText={setSerial}
      />
      <Pressable style={styles.btn} disabled={loading} onPress={() => void handleScan(serial)}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Submit</Text>}
      </Pressable>
      {error && <Text style={styles.error}>{error}</Text>}
      {result && (
        <View style={styles.result}>
          <Text style={styles.resultTitle}>Outcome: {result.outcome_label}</Text>
          {confidence && <Text style={styles.meta}>Confidence: {confidence} · risk {result.risk_score}</Text>}
          {result.alerts?.counterfeit_warning && (
            <Text style={styles.warn}>⚠ Suspicious / counterfeit signal</Text>
          )}
          {result.alerts?.recall_alert && <Text style={styles.warn}>Recall alert active</Text>}
          <Pressable onPress={() => void askAi()}>
            <Text style={styles.link}>AI explain scan (manual)</Text>
          </Pressable>
          <Pressable onPress={clear}>
            <Text style={styles.link}>Clear</Text>
          </Pressable>
        </View>
      )}
      {aiText && (
        <View style={styles.aiBox}>
          <Text style={styles.disclaimer}>AI-assisted — requires human review.</Text>
          <Text style={styles.aiText}>{aiText}</Text>
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  container: { gap: 8 },
  title: { fontSize: 18, fontWeight: "600", color: "#f8fafc" },
  hint: { fontSize: 12, color: "#64748b" },
  overlayBox: { height: 240, borderRadius: 12, overflow: "hidden", backgroundColor: "#0f172a" },
  overlayFrame: {
    ...StyleSheet.absoluteFillObject,
    borderWidth: 2,
    borderColor: "#38bdf844",
    borderRadius: 12,
    margin: 24,
  },
  row: { flexDirection: "row", justifyContent: "space-between" },
  link: { color: "#38bdf8", fontSize: 13 },
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
  error: { color: "#fca5a5" },
  result: { marginTop: 8, padding: 12, backgroundColor: "#1e293b", borderRadius: 8, gap: 6 },
  resultTitle: { color: "#f8fafc", fontWeight: "600" },
  meta: { color: "#94a3b8", fontSize: 12 },
  warn: { color: "#fbbf24", fontSize: 12 },
  aiBox: { marginTop: 8, padding: 10, backgroundColor: "#172554", borderRadius: 8 },
  disclaimer: { color: "#fbbf24", fontSize: 10 },
  aiText: { color: "#cbd5e1", fontSize: 12, marginTop: 4 },
});
