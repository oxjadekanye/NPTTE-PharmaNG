import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { useOfflineSync } from "@/hooks/useOfflineSync";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";
import type { SyncRunResult } from "@/services/offline-scan-sync";

export default function OfflineQueueScreen() {
  const { queue, syncAll, online } = useOfflineSync();
  const [syncing, setSyncing] = useState(false);
  const [result, setResult] = useState<SyncRunResult | null>(null);

  const pending = queue.filter(
    (q) => q.client_sync_status === "pending" || q.client_sync_status === "failed"
  );

  const handleRetryAll = async () => {
    mobileActionLog("retry_sync_all_pressed");
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
        message: err instanceof Error ? err.message : "Sync failed unexpectedly",
        attemptedAt: new Date().toISOString(),
      });
    } finally {
      setSyncing(false);
    }
  };

  return (
    <ScreenShell title="Offline scan queue" subtitle="Pending uploads sync via /scanning/sync-pending/">
      {!online && <Text style={styles.warn}>You are offline</Text>}
      <Pressable
        style={[styles.btn, syncing && styles.btnDisabled]}
        onPress={handleRetryAll}
        disabled={syncing}
        accessibilityRole="button"
        accessibilityLabel="Retry sync all"
      >
        {syncing ? (
          <View style={styles.btnRow}>
            <ActivityIndicator color="#fff" size="small" />
            <Text style={styles.btnText}>Syncing…</Text>
          </View>
        ) : (
          <Text style={styles.btnText}>Retry sync all</Text>
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
          {"\n"}
          Last attempt: {new Date(result.attemptedAt).toLocaleString()}
        </Text>
      ) : null}
      {pending.map((item) => (
        <View key={item.id} style={styles.row}>
          <Text style={styles.serial}>{item.serial_number}</Text>
          <Text style={styles.meta}>
            {item.scan_type} · {item.client_sync_status}
            {item.last_error ? ` · ${item.last_error}` : ""}
          </Text>
        </View>
      ))}
      {queue.length === 0 && <Text style={styles.empty}>No pending scans to sync</Text>}
      {queue.length > 0 && pending.length === 0 && !syncing && (
        <Text style={styles.empty}>All scans synced</Text>
      )}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  warn: { color: "#fbbf24", marginBottom: 12 },
  btn: {
    backgroundColor: "#0284c7",
    padding: 12,
    borderRadius: 8,
    alignItems: "center",
    marginBottom: 16,
    minHeight: 44,
    justifyContent: "center",
  },
  btnDisabled: { opacity: 0.6 },
  btnRow: { flexDirection: "row", alignItems: "center", gap: 8 },
  btnText: { color: "#fff", fontWeight: "600" },
  result: { fontSize: 12, marginBottom: 12, lineHeight: 18 },
  resultOk: { color: "#86efac" },
  resultWarn: { color: "#fbbf24" },
  row: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
  },
  serial: { color: "#f8fafc", fontWeight: "600" },
  meta: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
  empty: { color: "#64748b" },
});
