import { useMemo, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import {
  checklistFallbackRecommendation,
  mobileCopilot,
  parseCopilotText,
} from "@/services/mobile-ai";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";

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
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiSource, setAiSource] = useState<"api" | "fallback" | null>(null);

  const score = useMemo(() => {
    const total = SECTIONS.reduce((n, s) => n + s.items.length, 0);
    const done = Object.values(checks).filter(Boolean).length;
    return total ? Math.round((done / total) * 100) : 0;
  }, [checks]);

  const toggle = (key: string) => setChecks((c) => ({ ...c, [key]: !c[key] }));

  const aiRecommend = async () => {
    mobileActionLog("ai_recommendation_pressed", `score=${score}`);
    if (aiLoading) return;
    setAiLoading(true);
    setAiError(null);
    setAiRec(null);
    setAiSource(null);
    try {
      const res = await mobileCopilot({
        prompt_mode: "operational_recommendations",
        context_key: "open_alerts",
        user_question: `Field inspection checklist score ${score}%. Recommend enforcement actions.`,
      });
      const text = parseCopilotText(res.data);
      if (res.success && text) {
        setAiRec(text);
        setAiSource("api");
        return;
      }
      const fallback = checklistFallbackRecommendation(score);
      setAiRec(fallback);
      setAiSource("fallback");
      setAiError(res.message ? `API: ${res.message} — showing offline guidance` : "Using offline guidance");
    } catch (err) {
      const fallback = checklistFallbackRecommendation(score);
      setAiRec(fallback);
      setAiSource("fallback");
      setAiError(err instanceof Error ? err.message : "AI request failed");
    } finally {
      setAiLoading(false);
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
                <Text style={styles.item}>
                  {checks[key] ? "✓ " : "○ "}
                  {item}
                </Text>
              </Pressable>
            );
          })}
        </View>
      ))}
      <Pressable
        style={[styles.btn, aiLoading && styles.btnDisabled]}
        onPress={aiRecommend}
        disabled={aiLoading}
        accessibilityRole="button"
        accessibilityLabel="AI inspection recommendation"
      >
        {aiLoading ? (
          <View style={styles.btnRow}>
            <ActivityIndicator color="#fff" size="small" />
            <Text style={styles.btnText}>Generating recommendation…</Text>
          </View>
        ) : (
          <Text style={styles.btnText}>AI inspection recommendation</Text>
        )}
      </Pressable>
      {aiRec ? (
        <View style={styles.aiBox}>
          <Text style={styles.aiLabel}>
            {aiSource === "fallback" ? "Guidance (offline fallback)" : "AI recommendation"}
          </Text>
          <Text style={styles.ai}>{aiRec}</Text>
        </View>
      ) : null}
      {aiError ? <Text style={styles.aiErr}>{aiError}</Text> : null}
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
  btn: {
    backgroundColor: "#0284c7",
    padding: 12,
    borderRadius: 8,
    marginTop: 8,
    minHeight: 44,
    justifyContent: "center",
  },
  btnDisabled: { opacity: 0.6 },
  btnRow: { flexDirection: "row", alignItems: "center", justifyContent: "center", gap: 8 },
  btnText: { color: "#fff", textAlign: "center" },
  aiBox: { marginTop: 10, padding: 10, backgroundColor: "#1e293b", borderRadius: 8 },
  aiLabel: { color: "#38bdf8", fontSize: 11, marginBottom: 4 },
  ai: { color: "#cbd5e1", fontSize: 12, lineHeight: 18 },
  aiErr: { color: "#fbbf24", marginTop: 6, fontSize: 11 },
  sign: { color: "#64748b", fontSize: 11, marginTop: 12 },
});
