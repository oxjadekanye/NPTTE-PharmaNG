import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { fetchScanHistory } from "@/services/scanning";

export default function WarehouseTimeline() {
  const [scans, setScans] = useState<{ serial_number: string; outcome_label: string }[]>([]);

  useEffect(() => {
    fetchScanHistory().then((r) => {
      if (r.success && r.data?.scans) {
        setScans(
          r.data.scans.map((s) => ({
            serial_number: s.serial_number,
            outcome_label: s.outcome_label,
          }))
        );
      }
    });
  }, []);

  return (
    <ScreenShell title="Custody timeline" subtitle="Recent warehouse scans">
      {scans.map((s, i) => (
        <View key={i} style={styles.row}>
          <Text style={styles.serial}>{s.serial_number}</Text>
          <Text style={styles.meta}>{s.outcome_label}</Text>
        </View>
      ))}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  row: { paddingVertical: 10, borderBottomWidth: 1, borderBottomColor: "#1e293b" },
  serial: { color: "#f8fafc" },
  meta: { color: "#94a3b8", fontSize: 12 },
});
