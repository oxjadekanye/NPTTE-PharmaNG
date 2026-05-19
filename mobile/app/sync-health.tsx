import { Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { useEvidenceQueue } from "@/store/evidence-queue";

export default function SyncHealthScreen() {
  const { online, pendingCount, failedCount, syncAll, queue, lastSyncAt } = useOfflineSync();
  const evidenceQueue = useEvidenceQueue((s) => s.queue);
  const evidenceLastSync = useEvidenceQueue((s) => s.lastSyncAt);

  return (
    <ScreenShell title="Sync health" subtitle="Diagnostics for field operations">
      <View style={styles.card}>
        <Text style={styles.label}>Network</Text>
        <Text style={styles.value}>{online ? "Online" : "Offline"}</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.label}>Scan queue</Text>
        <Text style={styles.value}>
          {pendingCount} pending · {failedCount} failed
        </Text>
        <Text style={styles.sub}>Last sync: {lastSyncAt ? new Date(lastSyncAt).toLocaleString() : "Never"}</Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.label}>Evidence queue</Text>
        <Text style={styles.value}>{evidenceQueue.length} items</Text>
        <Text style={styles.sub}>
          Last sync: {evidenceLastSync ? new Date(evidenceLastSync).toLocaleString() : "Never"}
        </Text>
      </View>
      <Pressable style={styles.btn} onPress={() => void syncAll()}>
        <Text style={styles.btnText}>Retry scan sync (backoff)</Text>
      </Pressable>
      {queue
        .filter((q) => q.client_sync_status === "failed")
        .map((q) => (
          <Text key={q.id} style={styles.fail}>
            {q.serial_number}: {q.last_error}
          </Text>
        ))}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  card: { backgroundColor: "#1e293b", padding: 12, borderRadius: 8, marginBottom: 10 },
  label: { color: "#94a3b8", fontSize: 11 },
  value: { color: "#f8fafc", fontWeight: "600", marginTop: 4 },
  sub: { color: "#64748b", fontSize: 10, marginTop: 4 },
  btn: { backgroundColor: "#0284c7", padding: 14, borderRadius: 8, marginTop: 8 },
  btnText: { color: "#fff", fontWeight: "600", textAlign: "center" },
  fail: { color: "#fca5a5", fontSize: 11, marginTop: 6 },
});
