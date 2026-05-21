import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { publicVerify } from "@/services/citizen";

export default function CitizenManual() {
  const [serial, setSerial] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<Record<string, unknown> | null>(null);
  const [error, setError] = useState<string | null>(null);

  const verify = async () => {
    const trimmed = serial.trim();
    if (!trimmed) {
      setError("Enter a serial number to verify.");
      return;
    }
    setLoading(true);
    setError(null);
    setResult(null);
    const res = await publicVerify({ serial_number: trimmed });
    setLoading(false);
    if (!res.success) {
      setError(
        res.message || "Verification failed. Check network or confirm the public API is available."
      );
      return;
    }
    setResult(res.data ?? null);
  };

  return (
    <ScreenShell title="Manual lookup" subtitle="POST /public/verify/ (no login required)">
      <TextInput
        style={styles.input}
        placeholder="Serial number"
        placeholderTextColor="#64748b"
        value={serial}
        onChangeText={setSerial}
        editable={!loading}
        autoCapitalize="characters"
      />
      <Pressable style={styles.btn} onPress={() => void verify()} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Verify</Text>}
      </Pressable>
      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.error}>{error}</Text>
        </View>
      )}
      {result && (
        <View style={styles.result}>
          <Text style={styles.outcome}>Outcome: {String(result.outcome ?? "unknown")}</Text>
          <Text style={styles.muted}>{String(result.message ?? "")}</Text>
        </View>
      )}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
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
    marginTop: 12,
  },
  btnText: { color: "#fff", fontWeight: "600" },
  errorBox: { marginTop: 12, padding: 12, backgroundColor: "#450a0a", borderRadius: 8 },
  error: { color: "#fca5a5" },
  result: { marginTop: 16, padding: 12, backgroundColor: "#1e293b", borderRadius: 8 },
  outcome: { color: "#f8fafc", fontWeight: "600" },
  muted: { color: "#94a3b8", marginTop: 4 },
});
