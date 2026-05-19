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
    setLoading(true);
    setError(null);
    const res = await publicVerify({ serial_number: serial.trim() });
    setLoading(false);
    if (!res.success) {
      setError(res.message);
      return;
    }
    setResult(res.data ?? null);
  };

  return (
    <ScreenShell title="Manual lookup" subtitle="POST /public/verify/">
      <TextInput
        style={styles.input}
        placeholder="Serial number"
        placeholderTextColor="#64748b"
        value={serial}
        onChangeText={setSerial}
      />
      <Pressable style={styles.btn} onPress={() => void verify()} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Verify</Text>}
      </Pressable>
      {error && <Text style={styles.error}>{error}</Text>}
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
  error: { color: "#fca5a5", marginTop: 8 },
  result: { marginTop: 16, padding: 12, backgroundColor: "#1e293b", borderRadius: 8 },
  outcome: { color: "#f8fafc", fontWeight: "600" },
  muted: { color: "#94a3b8", marginTop: 4 },
});
