import { useMemo, useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { mobileCopilot } from "@/services/mobile-ai";

type Section = { id: string; title: string; items: string[] };

const SECTIONS: Section[] = [
  {
    id: "site",
    title: "Site verification",
    items: ["Registration displayed", "Storage conditions", "Staff interviewed"],
  },
  {
    id: "product",
    title: "Product verification",
    items: ["Serial samples scanned", "Batch records reviewed", "Expiry checks"],
  },
  {
    id: "compliance",
    title: "Compliance",
    items: ["Cold-chain logs", "Custody documentation", "Recall acknowledgement"],
  },
];

export function InspectionChecklistEngine() {
  const [checks, setChecks] = useState<Record<string, boolean>>({});
  const [aiRec, setAiRec] = useState<string | null>(null);

  const score = useMemo(() => {
    const total = SECTIONS.reduce((n, s) => n + s.items.length, 0);
    const done = Object.values(checks).filter(Boolean).length;
    return total ? Math.round((done / total) * 100) : 0;
  }, [checks]);

  const toggle = (key: string) => setChecks((c) => ({ ...c, [key]: !c[key] }));

  const aiRecommend = async () => {
    const res = await mobileCopilot({
      prompt_mode: "operational_recommendations",
      context_key: "open_alerts",
      user_question: `Field inspection checklist score ${score}%. Recommend enforcement actions.`,
    });
    if (res.success && res.data) {
      setAiRec(String(res.data.summary));
    }
  };

  return (
    <View>
      <Text style={styles.score}>Compliance score: {score}%</Text>
      {SECTIONS.map((sec) => (
        <View key={sec.id} style={styles.section}>
          <Text style={styles.sectionTitle}>{sec.title}</Text>
          {sec.items.map((item) => {
            const key = `${sec.id}:${item}`;
            return (
              <Pressable key={key} style={styles.row} onPress={() => toggle(key)}>
                <Text style={styles.item}>{checks[key] ? "✓ " : "○ "}{item}</Text>
              </Pressable>
            );
          })}
        </View>
      ))}
      <Pressable style={styles.btn} onPress={() => void aiRecommend()}>
        <Text style={styles.btnText}>AI inspection recommendation</Text>
      </Pressable>
      {aiRec && <Text style={styles.ai}>{aiRec}</Text>}
      <Text style={styles.sign}>Officer signature — capture on web enforcement record</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  score: { color: "#4ade80", fontWeight: "700", marginBottom: 12 },
  section: { marginBottom: 12 },
  sectionTitle: { color: "#38bdf8", fontSize: 13, marginBottom: 6 },
  row: { paddingVertical: 6 },
  item: { color: "#e2e8f0", fontSize: 13 },
  btn: { backgroundColor: "#0284c7", padding: 12, borderRadius: 8, marginTop: 8 },
  btnText: { color: "#fff", textAlign: "center" },
  ai: { color: "#cbd5e1", marginTop: 8, fontSize: 12 },
  sign: { color: "#64748b", fontSize: 11, marginTop: 12 },
});
