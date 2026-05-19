import { Pressable, StyleSheet, Text, View } from "react-native";
import { useOfflineSync } from "@/hooks/useOfflineSync";

export function OfflineBanner() {
  const { online, pendingCount, syncAll } = useOfflineSync();

  if (online && pendingCount === 0) return null;

  return (
    <View style={[styles.banner, !online ? styles.offline : styles.pending]}>
      <Text style={styles.text}>
        {!online
          ? "Offline — scans will queue until connectivity returns"
          : `${pendingCount} scan(s) waiting to sync`}
      </Text>
      {online && pendingCount > 0 && (
        <Pressable onPress={() => void syncAll()}>
          <Text style={styles.action}>Sync now</Text>
        </Pressable>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  banner: { padding: 10, paddingHorizontal: 16 },
  offline: { backgroundColor: "#7f1d1d" },
  pending: { backgroundColor: "#78350f" },
  text: { color: "#fef3c7", fontSize: 12 },
  action: { color: "#38bdf8", fontSize: 12, marginTop: 4, fontWeight: "600" },
});
