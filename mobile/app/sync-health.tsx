import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { useEvidenceQueue } from "@/store/evidence-queue";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";
import type { SyncRunResult } from "@/services/offline-scan-sync";

export default function SyncHealthScreen() {
  const { online, pendingCount, failedCount, syncAll, queue, lastSyncAt } = useOfflineSync();
  const evidenceQueue = useEvidenceQueue((s) => s.queue);
  const evidenceLastSync = useEvidenceQueue((s) => s.lastSyncAt);
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState<SyncRunResult | null>(null);

  const handleRetryScanSync = async () => {
    mobileActionLog("retry_scan_sync_pressed");
    if (syncing) return;
    setSyncing(true);
    setResult(null);
    try {
      const res = await syncAll();
      setResult(res);
    } catch (err) {
      setResult({
        synced: 0,
        failed: 0,
        attempted: 0,
        message: err instanceof Error ? err.message : "Scan sync failed unexpectedly",
        attemptedAt: new Date().toISOString(),
      });
    } finally {
      setSyncing(false);
    }
  };

  const displayLastSync = result?.attemptedAt ?? lastSyncAt;

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
        <Text style={styles.sub}>
          Last sync: {displayLastSync ? new Date(displayLastSync).toLocaleString() : "Never"}
        </Text>
      </View>
      <View style={styles.card}>
        <Text style={styles.label}>Evidence queue</Text>
        <Text style={styles.value}>{evidenceQueue.length} items</Text>
        <Text style={styles.sub}>
          Last sync: {evidenceLastSync ? new Date(evidenceLastSync).toLocaleString() : "Never"}
        </Text>
      </View>
      <Pressable
        style={[styles.btn, syncing && styles.btnDisabled]}
        onPress={handleRetryScanSync}
        disabled={syncing}
        accessibilityRole="button"
        accessibilityLabel="Retry scan sync"
      >
        {syncing ? (
          <View style={styles.btnRow}>
            <ActivityIndicator color="#fff" size="small" />
            <Text style={styles.btnText}>Syncing scans…</Text>
          </View>
        ) : (
          <Text style={styles.btnText}>Retry scan sync (backoff)</Text>
        )}
      </Pressable>
      {result ? (
        <Text
          style={[
            styles.result,
            result.error === "offline" || result.failed > 0 ? styles.resultWarn : styles.resultOk,
          ]}
        >
          {result.message}
        </Text>
      ) : null}
      {queue
        .filter((q) => q.client_sync_status === "failed")
        .map((q) => (
          <Text key={q.id} style={styles.fail}>
            {q.serial_number}: {q.last_error ?? "Unknown error"}
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
  btn: {
    backgroundColor: "#0284c7",
    padding: 14,
    borderRadius: 8,
    marginTop: 8,
    minHeight: 44,
    justifyContent: "center",
  },
  btnDisabled: { opacity: 0.6 },
  btnRow: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8 },
  btnText: { color: "#fff", fontWeight: "600", textAlign: "center" },
  result: { fontSize: 12, marginTop: 10, lineHeight: 18 },
  resultOk: { color: "#86efac" },
  resultWarn: { color: "#fbbf24" },
  fail: { color: "#fca5a5", fontSize: 11, marginTop: 6 },
});
