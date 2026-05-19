import { Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { useOfflineSync } from "@/hooks/useOfflineSync";

export default function OfflineQueueScreen() {
  const { queue, syncAll, online } = useOfflineSync();

  return (
    <ScreenShell title="Offline scan queue" subtitle="Pending uploads sync via /scanning/sync-pending/">
      {!online && <Text style={styles.warn}>You are offline</Text>}
      <Pressable style={styles.btn} onPress={() => void syncAll()}>
        <Text style={styles.btnText}>Retry sync all</Text>
      </Pressable>
      {queue.map((item) => (
        <View key={item.id} style={styles.row}>
          <Text style={styles.serial}>{item.serial_number}</Text>
          <Text style={styles.meta}>
            {item.scan_type} · {item.client_sync_status}
            {item.last_error ? ` · ${item.last_error}` : ""}
          </Text>
        </View>
      ))}
      {queue.length === 0 && <Text style={styles.empty}>Queue empty</Text>}
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
  },
  btnText: { color: "#fff", fontWeight: "600" },
  row: {
    padding: 12,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
  },
  serial: { color: "#f8fafc", fontWeight: "600" },
  meta: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
  empty: { color: "#64748b" },
});
