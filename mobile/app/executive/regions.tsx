import { useEffect, useState } from "react";
import { StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { fetchRegionalList } from "@/services/executive";
import { apiRequest } from "@/services/api-client";

export default function ExecutiveRegions() {
  const [regions, setRegions] = useState<{ key: string; label: string; hint?: string }[]>([]);

  useEffect(() => {
    fetchRegionalList().then(async (r) => {
      if (!r.success || !r.data?.regions) return;
      const enriched = await Promise.all(
        r.data.regions.map(async (reg) => {
          const detail = await apiRequest<Record<string, unknown>>(
            `/command-orchestration/regions/${reg.key}/`
          );
          return {
            ...reg,
            hint: detail.success ? String(detail.data?.ai_summary_hint ?? "") : "",
          };
        })
      );
      setRegions(enriched);
    });
  }, []);

  return (
    <ScreenShell title="Regional summary" subtitle="Six geopolitical zones">
      {regions.map((reg) => (
        <View key={reg.key} style={styles.card}>
          <Text style={styles.title}>{reg.label}</Text>
          <Text style={styles.hint}>{reg.hint}</Text>
        </View>
      ))}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: "#1e293b",
    padding: 12,
    borderRadius: 8,
    marginBottom: 10,
  },
  title: { color: "#f8fafc", fontWeight: "600" },
  hint: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
});
