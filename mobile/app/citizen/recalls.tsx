import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { fetchPublicRecalls } from "@/services/citizen";

export default function CitizenRecalls() {
  const [recalls, setRecalls] = useState<unknown[]>([]);

  useEffect(() => {
    fetchPublicRecalls().then((r) => {
      if (r.success && r.data?.recalls) setRecalls(r.data.recalls);
    });
  }, []);

  return (
    <ScreenShell title="Recall alerts" subtitle="National recall feed">
      {recalls.map((item, i) => (
        <View key={i} style={styles.row}>
          <Text style={styles.text}>{JSON.stringify(item)}</Text>
        </View>
      ))}
      {recalls.length === 0 && <Text style={styles.empty}>No active recalls</Text>}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  row: { paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: "#1e293b" },
  text: { color: "#cbd5e1", fontSize: 12 },
  empty: { color: "#64748b" },
});
