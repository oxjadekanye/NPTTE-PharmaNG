import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { fetchPublicRecalls } from "@/services/citizen";

export default function CitizenRecalls() {
  const [recalls, setRecalls] = useState<unknown[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    setLoading(true);
    setError(null);
    const res = await fetchPublicRecalls();
    setLoading(false);
    if (!res.success) {
      setError(res.message || "Could not load recalls. Check network connection.");
      return;
    }
    setRecalls(res.data?.recalls ?? []);
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  return (
    <ScreenShell title="Recall alerts" subtitle="National recall feed (public API)">
      {loading && <ActivityIndicator color="#38bdf8" style={styles.loader} />}
      {error && (
        <View style={styles.errorBox}>
          <Text style={styles.error}>{error}</Text>
          <Pressable style={styles.retry} onPress={() => void load()}>
            <Text style={styles.retryText}>Retry</Text>
          </Pressable>
        </View>
      )}
      {!loading &&
        !error &&
        recalls.map((item, i) => (
          <View key={i} style={styles.row}>
            <Text style={styles.text}>{JSON.stringify(item)}</Text>
          </View>
        ))}
      {!loading && !error && recalls.length === 0 && (
        <Text style={styles.empty}>No active recalls</Text>
      )}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  loader: { marginVertical: 16 },
  errorBox: { marginTop: 12, padding: 12, backgroundColor: "#450a0a", borderRadius: 8 },
  error: { color: "#fca5a5", fontSize: 13 },
  retry: {
    marginTop: 10,
    backgroundColor: "#0ea5e9",
    padding: 10,
    borderRadius: 8,
    alignItems: "center",
  },
  retryText: { color: "#fff", fontWeight: "600" },
  row: { paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: "#1e293b" },
  text: { color: "#cbd5e1", fontSize: 12 },
  empty: { color: "#64748b", marginTop: 12 },
});
