import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { fetchMobileAuditTimeline } from "@/services/audit";

export default function FieldActivityScreen() {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);

  useEffect(() => {
    fetchMobileAuditTimeline().then((r) => {
      if (r.success && r.data?.timeline) setRows(r.data.timeline);
    });
  }, []);

  return (
    <ScreenShell title="Field activity" subtitle="Mobile operational audit trail">
      {rows.map((r) => (
        <View key={String(r.id)} style={styles.row}>
          <Text style={styles.type}>{String(r.action_type)}</Text>
          <Text style={styles.meta}>{new Date(String(r.created_at)).toLocaleString()}</Text>
        </View>
      ))}
      {rows.length === 0 && <Text style={styles.empty}>No activity yet</Text>}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  row: { paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: "#1e293b" },
  type: { color: "#f8fafc", fontWeight: "600" },
  meta: { color: "#94a3b8", fontSize: 11, marginTop: 2 },
  empty: { color: "#64748b" },
});
