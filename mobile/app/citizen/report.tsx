import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { reportCounterfeit } from "@/services/citizen";

export default function CitizenReport() {
  const [description, setDescription] = useState("");
  const [serial, setSerial] = useState("");
  const [msg, setMsg] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  const submit = async () => {
    const trimmedDesc = description.trim();
    if (!trimmedDesc) {
      setError("Enter a description of what you found.");
      return;
    }
    setLoading(true);
    setError(null);
    setMsg(null);
    const res = await reportCounterfeit({
      description: trimmedDesc,
      serial_number: serial.trim() || undefined,
    });
    setLoading(false);
    if (!res.success) {
      setError(res.message || "Report failed. Check network and try again.");
      return;
    }
    setMsg("Report submitted — thank you");
    setDescription("");
    setSerial("");
  };

  return (
    <ScreenShell title="Report suspicious medicine" subtitle="National counterfeit reporting">
      <TextInput
        style={styles.input}
        placeholder="Describe what you found"
        placeholderTextColor="#64748b"
        multiline
        value={description}
        onChangeText={setDescription}
        editable={!loading}
      />
      <TextInput
        style={styles.input}
        placeholder="Serial (optional)"
        placeholderTextColor="#64748b"
        value={serial}
        onChangeText={setSerial}
        editable={!loading}
      />
      <Pressable style={styles.btn} onPress={() => void submit()} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Submit report</Text>}
      </Pressable>
      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.error}>{error}</Text>
        </View>
      )}
      {msg && <Text style={styles.msg}>{msg}</Text>}
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
    marginBottom: 12,
    backgroundColor: "#0f172a",
    minHeight: 80,
  },
  btn: {
    backgroundColor: "#b91c1c",
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  btnText: { color: "#fff", fontWeight: "600" },
  errorBox: { marginTop: 12, padding: 12, backgroundColor: "#450a0a", borderRadius: 8 },
  error: { color: "#fca5a5" },
  msg: { color: "#86efac", marginTop: 12 },
});
