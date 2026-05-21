import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { InspectionChecklistEngine } from "@/components/InspectionChecklistEngine";
import { EvidenceCapture } from "@/components/EvidenceCapture";
import { apiRequest } from "@/services/api-client";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";

const STEPS = ["Site", "Product", "Compliance", "Evidence", "Sign-off"] as const;

export default function InspectionModeScreen() {
  const [step, setStep] = useState(0);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [status, setStatus] = useState<string | null>(null);

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
          checklist_score: 75,
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
            onPress={() => setStep(i)}
          >
            <Text style={styles.stepText}>{s}</Text>
          </Pressable>
        ))}
      </View>
      {!taskId && (
        <Pressable style={styles.btn} onPress={() => void startInspection()} disabled={loading}>
          {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Start inspection</Text>}
        </Pressable>
      )}
      {step <= 2 && <InspectionChecklistEngine />}
      {step === 3 && <EvidenceCapture evidenceType="inspection" />}
      {step === 4 && (
        <Pressable style={styles.btn} onPress={() => void completeInspection()} disabled={loading}>
          <Text style={styles.btnText}>Submit completion report</Text>
        </Pressable>
      )}
      {status ? <Text style={styles.status}>{status}</Text> : null}
      {taskId ? <Text style={styles.meta}>Task {taskId}</Text> : null}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  steps: { flexDirection: "row", flexWrap: "wrap", gap: 6, marginBottom: 12 },
  step: { padding: 8, borderRadius: 8, backgroundColor: "#1e293b" },
  stepActive: { backgroundColor: "#0284c7" },
  stepText: { color: "#e2e8f0", fontSize: 11 },
  btn: { backgroundColor: "#0284c7", padding: 12, borderRadius: 8, alignItems: "center", marginVertical: 8 },
  btnText: { color: "#fff", fontWeight: "600" },
  status: { color: "#86efac", marginTop: 8 },
  meta: { color: "#64748b", fontSize: 10, marginTop: 4 },
});
