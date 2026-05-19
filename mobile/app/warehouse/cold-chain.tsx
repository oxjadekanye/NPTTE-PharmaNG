import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { mobileCopilot } from "@/services/mobile-ai";
import { useMobileRealtime } from "@/hooks/useMobileRealtime";

export default function WarehouseColdChain() {
  const [loading, setLoading] = useState(false);
  const [summary, setSummary] = useState<string | null>(null);
  const { events } = useMobileRealtime("warehouse", true);

  const spoilageSummary = async () => {
    setLoading(true);
    const res = await mobileCopilot({
      prompt_mode: "explain_risk",
      user_question: "Summarize cold-chain spoilage risk for warehouse field officer.",
    });
    setLoading(false);
    if (res.success && res.data) setSummary(String(res.data.summary));
  };

  return (
    <ScreenShell title="Cold-chain breach" subtitle="Alerts from scans and streambus">
      <Text style={styles.body}>
        Breach scans surface through warehouse_receive with critical severity. National alerts
        propagate to command dashboards in realtime.
      </Text>
      <Pressable style={styles.btn} onPress={() => void spoilageSummary()} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>AI spoilage risk summary</Text>
        )}
      </Pressable>
      {summary && <Text style={styles.ai}>{summary}</Text>}
      {events.length > 0 && (
        <Text style={styles.live}>Latest alert: {String(events[0].event_type ?? "update")}</Text>
      )}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  body: { color: "#94a3b8", marginBottom: 16, lineHeight: 20 },
  btn: { backgroundColor: "#0284c7", padding: 14, borderRadius: 8, alignItems: "center" },
  btnText: { color: "#fff", fontWeight: "600" },
  ai: { color: "#e2e8f0", marginTop: 12, fontSize: 12 },
  live: { color: "#38bdf8", marginTop: 16, fontSize: 11 },
});
