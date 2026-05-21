import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { apiRequest } from "@/services/api-client";

export default function SeizureWorkflowScreen() {
  const [notes, setNotes] = useState("");
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

  const submit = async () => {
    setLoading(true);
    try {
      const res = await apiRequest("/mobile/field/seizure/", {
        method: "POST",
        body: JSON.stringify({ title: "Field seizure", notes, escalate: true }),
      });
      setStatus(res.success ? "Seizure workflow recorded" : res.message);
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenShell title="Seizure workflow" subtitle="Enforcement escalation with GPS evidence">
      <TextInput
        style={styles.input}
        placeholder="Seizure notes"
        placeholderTextColor="#64748b"
        value={notes}
        onChangeText={setNotes}
        multiline
      />
      <Pressable style={styles.btn} onPress={() => void submit()} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Record seizure & escalate</Text>}
      </Pressable>
      {status ? <Text style={styles.status}>{status}</Text> : null}
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
    minHeight: 80,
    marginBottom: 12,
  },
  btn: { backgroundColor: "#b45309", padding: 14, borderRadius: 8, alignItems: "center" },
  btnText: { color: "#fff", fontWeight: "700" },
  status: { color: "#86efac", marginTop: 12 },
});
