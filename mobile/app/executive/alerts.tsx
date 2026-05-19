import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { fetchCommandRoomSnapshot } from "@/services/executive";

export default function ExecutiveAlerts() {
  const [events, setEvents] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    fetchCommandRoomSnapshot().then((r) => {
      if (r.success && r.data?.live_events) {
        setEvents(r.data.live_events as Record<string, unknown>[]);
      }
    });
  }, []);

  return (
    <ScreenShell title="Urgent alerts" subtitle="Live streambus snapshot">
      {events.slice(0, 15).map((e, i) => (
        <View key={i} style={styles.row}>
          <Text style={styles.text}>{String(e.event_type ?? e.summary ?? "event")}</Text>
        </View>
      ))}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  row: { paddingVertical: 8, borderBottomWidth: 1, borderBottomColor: "#1e293b" },
  text: { color: "#cbd5e1", fontSize: 12 },
});
