import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { apiRequest } from "@/services/api-client";

export default function RegulatorNote() {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);

  const draft = async () => {
    setLoading(true);
    const res = await apiRequest<Record<string, unknown>>("/copilot/draft-enforcement-note/", {
      method: "POST",
      body: JSON.stringify({
        context_key: "open_alerts",
        prompt_mode: "draft_enforcement_note",
      }),
    });
    setLoading(false);
    if (res.success && res.data) {
      setSummary(String(res.data.summary ?? "") + "\n\n" + String(res.data.reasoning ?? ""));
    }
  };

  return (
    <ScreenShell title="Enforcement note" subtitle="AI-assisted — manual trigger only">
      <Pressable style={styles.btn} onPress={() => void draft()} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Generate draft note</Text>
        )}
      </Pressable>
      {summary && <Text style={styles.note}>{summary}</Text>}
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
  note: { color: "#e2e8f0", marginTop: 16, lineHeight: 20 },
  disclaimer: { color: "#fbbf24", fontSize: 11, marginTop: 12 },
});
