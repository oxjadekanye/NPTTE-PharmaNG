import { useEffect, useState } from "react";
import { ActivityIndicator, StyleSheet, Text, View } from "react-native";
import { MenuButton } from "@/components/MenuButton";
import { ScreenShell } from "@/components/ScreenShell";
import { useMobileRealtime } from "@/hooks/useMobileRealtime";
import { fetchCommandRoomSnapshot } from "@/services/executive";

export default function ExecutiveHome() {
  const [readiness, setReadiness] = useState<string>("—");
  const [loading, setLoading] = useState(true);
  const { events } = useMobileRealtime("executive", true);

  useEffect(() => {
    fetchCommandRoomSnapshot().then((r) => {
      if (r.success && r.data) {
        setReadiness(String(r.data.national_readiness_index ?? "—"));
      }
      setLoading(false);
    });
  }, []);

  return (
    <ScreenShell title="Executive" subtitle="National monitoring — read only">
      {loading ? (
        <ActivityIndicator color="#38bdf8" />
      ) : (
        <View style={styles.card}>
          <Text style={styles.label}>National readiness</Text>
          <Text style={styles.value}>{readiness}</Text>
        </View>
      )}
      <MenuButton href="/executive/alerts" label="Urgent alerts" />
      <MenuButton href="/executive/briefing" label="AI briefing (manual)" />
      <MenuButton href="/executive/regions" label="Regional heat summary" />
      <MenuButton href="/settings" label="Settings" />
      {events.length > 0 && (
        <Text style={styles.feed}>Live feed: {String(events[0].event_type ?? "update")}</Text>
      )}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1e293b",
    padding: 16,
    borderRadius: 12,
    marginBottom: 16,
  },
  label: { color: "#94a3b8", fontSize: 12 },
  value: { color: "#4ade80", fontSize: 36, fontWeight: "700" },
  feed: { color: "#94a3b8", fontSize: 11, marginTop: 12 },
});
