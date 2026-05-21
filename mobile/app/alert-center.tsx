import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { useRealtimeFeed } from "@/hooks/useRealtimeFeed";
import { apiRequest } from "@/services/api-client";

export default function AlertCenterScreen() {
  const { feed, loading, refresh } = useRealtimeFeed("recall_alert,national_alert");
  const [center, setCenter] = useState<{ alerts: unknown[]; unread_count: number } | null>(null);

  const loadCenter = async () => {
    const res = await apiRequest<{ alerts: unknown[]; unread_count: number }>("/alerts/center/");
    if (res.success && res.data) setCenter(res.data);
  };

  return (
    <ScreenShell title="Alert center" subtitle="National operational notifications">
      <Pressable style={styles.btn} onPress={() => void Promise.all([refresh(), loadCenter()])}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Refresh alerts</Text>
        )}
      </Pressable>
      <Text style={styles.meta}>
        Feed: {(feed?.alerts?.length ?? 0) + (feed?.events?.length ?? 0)} items · polled{" "}
        {feed?.polled_at ? new Date(feed.polled_at).toLocaleTimeString() : "—"}
      </Text>
      {(center?.alerts ?? feed?.alerts ?? []).map((a, i) => {
        const row = a as { id?: string; title?: string; severity?: string };
        return (
          <View key={row.id ?? i} style={styles.row}>
            <Text style={styles.title}>{row.title ?? "Alert"}</Text>
            <Text style={styles.sub}>{row.severity ?? "INFO"}</Text>
          </View>
        );
      })}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  btn: { backgroundColor: "#0284c7", padding: 12, borderRadius: 8, alignItems: "center", marginBottom: 12 },
  btnText: { color: "#fff", fontWeight: "600" },
  meta: { color: "#94a3b8", fontSize: 11, marginBottom: 12 },
  row: { padding: 12, borderBottomWidth: 1, borderBottomColor: "#1e293b" },
  title: { color: "#f8fafc", fontWeight: "600" },
  sub: { color: "#94a3b8", fontSize: 11, marginTop: 4 },
});
