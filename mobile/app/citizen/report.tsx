import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { reportCounterfeit } from "@/services/citizen";

export default function CitizenReport() {
  const [description, setDescription] = useState("");
  const [serial, setSerial] = useState("");
  const [msg, setMsg] = useState<string | null>(null);

  const submit = async () => {
    const res = await reportCounterfeit({
      description,
      serial_number: serial || undefined,
    });
    setMsg(res.success ? "Report submitted — thank you" : res.message);
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
      />
      <TextInput
        style={styles.input}
        placeholder="Serial (optional)"
        placeholderTextColor="#64748b"
        value={serial}
        onChangeText={setSerial}
      />
      <Pressable style={styles.btn} onPress={() => void submit()}>
        <Text style={styles.btnText}>Submit report</Text>
      </Pressable>
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
  msg: { color: "#86efac", marginTop: 12 },
});
