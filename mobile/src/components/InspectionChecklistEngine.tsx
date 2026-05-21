import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import {
  formatInspectionRecommendation,
  inspectionRecommendationFallback,
  parseInspectionRecommendation,
} from "@/services/mobile-ai-helpers";
import { mobileInspectionCopilot } from "@/services/mobile-ai";
import {
  buildInspectionContext,
  computeInspectionScore,
  type InspectionSectionId,
  INSPECTION_SECTIONS,
  inspectionItemKey,
} from "@/services/mobile-inspection";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";

type Props = {
  activeSection: InspectionSectionId;
  checks: Record<string, boolean>;
  onToggle: (key: string) => void;
  evidenceCount?: number;
  organisationHint?: string;
};

export function InspectionChecklistEngine({
  activeSection,
  checks,
  onToggle,
  evidenceCount = 0,
  organisationHint,
}: Props) {
  const [aiRec, setAiRec] = useState<string | null>(null);
  const [aiLoading, setAiLoading] = useState(false);
  const [aiError, setAiError] = useState<string | null>(null);
  const [aiSource, setAiSource] = useState<"api" | "fallback" | null>(null);

  const score = computeInspectionScore(checks);
  const section = INSPECTION_SECTIONS.find((s) => s.id === activeSection);

  const aiRecommend = async () => {
    mobileActionLog("ai_inspection_recommendation_requested", `score=${score}`);
    if (aiLoading) return;
    setAiLoading(true);
    setAiError(null);
    setAiRec(null);
    setAiSource(null);
    const context = buildInspectionContext(checks, evidenceCount, organisationHint);
    try {
      const res = await mobileInspectionCopilot(context);
      const parsed = parseInspectionRecommendation(res.data);
      if (res.success && parsed) {
        setAiRec(formatInspectionRecommendation({ ...parsed, source: "api" }));
        setAiSource("api");
        return;
      }
      const fallback = inspectionRecommendationFallback(context);
      setAiRec(formatInspectionRecommendation(fallback));
      setAiSource("fallback");
      setAiError(res.message ? `API: ${res.message} — offline guidance` : "Using checklist-based guidance");
    } catch (err) {
      const fallback = inspectionRecommendationFallback(
        buildInspectionContext(checks, evidenceCount, organisationHint)
      );
      setAiRec(formatInspectionRecommendation(fallback));
      setAiSource("fallback");
      setAiError(err instanceof Error ? err.message : "AI request failed");
    } finally {
      setAiLoading(false);
    }
  };

  if (!section) {
    return <Text style={styles.empty}>Unknown inspection section</Text>;
  }

  const sectionDone = section.items.filter((item) => checks[inspectionItemKey(activeSection, item)]).length;
  const sectionTotal = section.items.length;

  return (
    <View>
      <Text style={styles.score}>Overall compliance: {score}%</Text>
      <Text style={styles.sectionHint}>
        {section.title} — {sectionDone}/{sectionTotal} checks complete
      </Text>
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>{section.title}</Text>
        {section.items.map((item) => {
          const key = inspectionItemKey(activeSection, item);
          return (
            <Pressable
              key={key}
              style={styles.row}
              onPress={() => onToggle(key)}
              accessibilityRole="checkbox"
              accessibilityState={{ checked: Boolean(checks[key]) }}
              accessibilityLabel={item}
            >
              <Text style={styles.item}>
                {checks[key] ? "✓ " : "○ "}
                {item}
              </Text>
            </Pressable>
          );
        })}
      </View>
      <Pressable
        style={[styles.btn, aiLoading && styles.btnDisabled]}
        onPress={() => void aiRecommend()}
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
            {aiSource === "fallback" ? "Guidance (checklist fallback)" : "AI recommendation"}
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
  score: { color: "#4ade80", fontWeight: "700", marginBottom: 4 },
  sectionHint: { color: "#94a3b8", fontSize: 12, marginBottom: 12 },
  section: { marginBottom: 12 },
  sectionTitle: { color: "#38bdf8", fontSize: 15, fontWeight: "700", marginBottom: 8 },
  row: { paddingVertical: 8 },
  item: { color: "#f8fafc", fontSize: 14 },
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
  btnText: { color: "#fff", textAlign: "center", fontWeight: "600" },
  aiBox: { marginTop: 10, padding: 12, backgroundColor: "#1e293b", borderRadius: 8, borderWidth: 1, borderColor: "#334155" },
  aiLabel: { color: "#38bdf8", fontSize: 11, marginBottom: 6, fontWeight: "600" },
  ai: { color: "#e2e8f0", fontSize: 13, lineHeight: 20 },
  aiErr: { color: "#fbbf24", marginTop: 6, fontSize: 11 },
  sign: { color: "#64748b", fontSize: 11, marginTop: 12 },
  empty: { color: "#94a3b8" },
});
