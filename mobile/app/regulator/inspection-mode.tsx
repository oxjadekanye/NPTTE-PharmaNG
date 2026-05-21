import { useMemo, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { InspectionChecklistEngine } from "@/components/InspectionChecklistEngine";
import { EvidenceCapture } from "@/components/EvidenceCapture";
import { apiRequest } from "@/services/api-client";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";
import {
  computeInspectionScore,
  type InspectionSectionId,
  INSPECTION_SECTIONS,
} from "@/services/mobile-inspection";

const STEPS = ["Site", "Product", "Compliance", "Evidence", "Sign-off"] as const;
const SECTION_BY_STEP: InspectionSectionId[] = ["site", "product", "compliance"];

export default function InspectionModeScreen() {
  const [step, setStep] = useState(0);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);
  const [checks, setChecks] = useState<Record<string, boolean>>({});
  const [evidenceCount, setEvidenceCount] = useState(0);

  const activeSection = SECTION_BY_STEP[step] ?? "site";
  const complianceScore = useMemo(() => computeInspectionScore(checks), [checks]);

  const setStepWithLog = (index: number) => {
    if (index === 1) mobileActionLog("inspection_tab_product_pressed");
    if (index === 2) mobileActionLog("inspection_tab_compliance_pressed");
    setStep(index);
  };

  const toggleCheck = (key: string) => {
    setChecks((c) => ({ ...c, [key]: !c[key] }));
  };

  const startInspection = async () => {
    mobileActionLog("ai_recommendation_pressed", "inspection_start");
    setLoading(true);
    try {
      const res = await apiRequest<{ task: { id: string } }>("/mobile/inspection/workflow/", {
        method: "POST",
        body: JSON.stringify({ action: "start", title: "Guided field inspection" }),
      });
      if (res.success && res.data?.task) {
        setTaskId(res.data.task.id);
        setStatus("Inspection workflow started");
      } else {
        setStatus(res.message || "Could not start inspection");
      }
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Start failed");
    } finally {
      setLoading(false);
    }
  };

  const completeInspection = async () => {
    setLoading(true);
    try {
      const res = await apiRequest("/mobile/inspection/workflow/", {
        method: "POST",
        body: JSON.stringify({
          action: "complete",
          checklist_score: complianceScore,
          violations: [],
          signature_note: "Captured on mobile field device",
        }),
      });
      setStatus(res.success ? "Inspection report submitted" : res.message);
    } catch (e) {
      setStatus(e instanceof Error ? e.message : "Complete failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenShell title="Field inspection mode" subtitle="Guided offline-capable workflow">
      <View style={styles.steps}>
        {STEPS.map((s, i) => (
          <Pressable
            key={s}
            style={[styles.step, i === step && styles.stepActive]}
            onPress={() => setStepWithLog(i)}
            accessibilityRole="tab"
            accessibilityState={{ selected: i === step }}
            accessibilityLabel={`${s} tab`}
          >
            <Text style={[styles.stepText, i === step && styles.stepTextActive]}>{s}</Text>
          </Pressable>
        ))}
      </View>
      <Text style={styles.activeTab}>
        Active: {STEPS[step]} · {INSPECTION_SECTIONS.find((x) => x.id === activeSection)?.title ?? STEPS[step]}
      </Text>
      {!taskId && (
        <Pressable style={styles.btn} onPress={() => void startInspection()} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Start inspection</Text>}
        </Pressable>
      )}
      {step <= 2 && (
        <InspectionChecklistEngine
          activeSection={activeSection}
          checks={checks}
          onToggle={toggleCheck}
          evidenceCount={evidenceCount}
        />
      )}
      {step === 3 && (
        <EvidenceCapture
          evidenceType="inspection"
          onCaptured={() => setEvidenceCount((n) => n + 1)}
        />
      )}
      {step === 4 && (
        <Pressable style={styles.btn} onPress={() => void completeInspection()} disabled={loading}>
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.btnText}>Submit completion report ({complianceScore}%)</Text>
          )}
        </Pressable>
      )}
      {status ? <Text style={styles.status}>{status}</Text> : null}
      {taskId ? <Text style={styles.meta}>Task {taskId}</Text> : null}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  steps: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginBottom: 8 },
  step: { padding: 8, borderRadius: 8, backgroundColor: "#1e293b", borderWidth: 1, borderColor: "#334155" },
  stepActive: { backgroundColor: "#0284c7", borderColor: "#38bdf8" },
  stepText: { color: "#94a3b8", fontSize: 11, fontWeight: "600" },
  stepTextActive: { color: "#ffffff" },
  activeTab: { color: "#38bdf8", fontSize: 12, marginBottom: 12, fontWeight: "600" },
  btn: { backgroundColor: "#0284c7", padding: 12, borderRadius: 8, alignItems: "center", marginVertical: 8 },
  btnText: { color: "#fff", fontWeight: "600" },
  status: { color: "#86efac", marginTop: 8 },
  meta: { color: "#64748b", fontSize: 10, marginTop: 4 },
});
