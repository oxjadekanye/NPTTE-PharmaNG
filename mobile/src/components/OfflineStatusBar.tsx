import { StyleSheet, Text, View } from "react-native";
import { useOfflineSync } from "@/hooks/useOfflineSync";

export function OfflineStatusBar() {
  const { online, pendingCount, failedCount, lastSyncAt } = useOfflineSync();

  if (online && pendingCount === 0 && failedCount === 0) return null;

  return (
    <View style={[styles.bar, !online ? styles.offline : styles.pending]}>
      <Text style={styles.text}>
        {!online
          ? "Offline — operations queued"
          : `${pendingCount} pending · ${failedCount} failed sync`}
      </Text>
      {lastSyncAt && <Text style={styles.sub}>Last sync: {new Date(lastSyncAt).toLocaleString()}</Text>}
    </View>
  );
}

const styles = StyleSheet.create({
  bar: { padding: 8, paddingHorizontal: 12 },
  offline: { backgroundColor: "#7f1d1d" },
  pending: { backgroundColor: "#78350f" },
  text: { color: "#fef3c7", fontSize: 11 },
  sub: { color: "#fcd34d", fontSize: 10, marginTop: 2 },
});
