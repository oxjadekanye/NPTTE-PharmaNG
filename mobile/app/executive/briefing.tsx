import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { fetchExecutiveBriefing } from "@/services/executive";

export default function ExecutiveBriefing() {
  const [loading, setLoading] = useState(false);
  const [text, setText] = useState<string | null>(null);

  const generate = async () => {
    setLoading(true);
    const res = await fetchExecutiveBriefing();
    setLoading(false);
    if (res.success && res.data) {
      setText(
        `${res.data.summary}\n\n${res.data.reasoning}\n\n${(res.data.recommended_actions as string[])?.join("\n• ") ?? ""}`
      );
    }
  };

  return (
    <ScreenShell title="AI briefing" subtitle="On-demand only — not automatic">
      <Pressable style={styles.btn} onPress={() => void generate()} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Generate briefing</Text>}
      </Pressable>
      {text && <Text style={styles.body}>{text}</Text>}
      <Text style={styles.disclaimer}>AI-assisted — requires human review.</Text>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  btn: {
    backgroundColor: "#0284c7",
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
  },
  btnText: { color: "#fff", fontWeight: "600" },
  body: { color: "#e2e8f0", marginTop: 16, lineHeight: 22 },
  disclaimer: { color: "#fbbf24", fontSize: 11, marginTop: 12 },
});
