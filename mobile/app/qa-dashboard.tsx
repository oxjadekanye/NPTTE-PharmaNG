import * as Application from "expo-application";
import Constants from "expo-constants";
import { router } from "expo-router";
import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { useMobileRealtime } from "@/hooks/useMobileRealtime";
import { useNetwork } from "@/hooks/useNetwork";
import { detectDeviceRiskFlags } from "@/services/device-trust";
import { listSimulations, runOperationalSimulation } from "@/services/operational-simulation";
import {
  getAverageApiLatency,
  getRecentMetrics,
  getStartupMs,
  sampleMemoryPlaceholder,
} from "@/services/performance-monitor";
import { CrashReporting } from "@/services/crash-reporting";
import { useEvidenceQueue } from "@/store/evidence-queue";
import { useOfflineQueue } from "@/store/offline-queue";
import { useQaMode } from "@/store/qa-mode-store";

export default function QaDashboardScreen() {
  const enabled = useQaMode((s) => s.enabled);
  const disable = useQaMode((s) => s.disable);
  const { online } = useNetwork();
  const queue = useOfflineQueue((s) => s.queue);
  const evidence = useEvidenceQueue((s) => s.queue);
  const { events, refresh } = useMobileRealtime("officer_tasks", enabled);
  const [trust, setTrust] = useState<string>("—");
  const [simBusy, setSimBusy] = useState<string | null>(null);

  useEffect(() => {
    if (!enabled) router.replace("/");
  }, [enabled]);

  const loadTrust = useCallback(() => {
    const flags = detectDeviceRiskFlags();
    const deviceId = useOfflineQueue.getState().deviceId || "unregistered";
    setTrust(`${deviceId.slice(0, 24)}… · ${flags.suspicious ? "review" : "ok"}`);
  }, []);

  useEffect(() => {
    loadTrust();
  }, [loadTrust]);

  if (!enabled) {
    return (
      <ScreenShell title="QA">
        <Text style={styles.muted}>QA mode not enabled.</Text>
      </ScreenShell>
    );
  }

  const extra = Constants.expoConfig?.extra ?? {};
  const metrics = getRecentMetrics(12);
  const avgApi = getAverageApiLatency();

  return (
    <ScreenShell title="Device QA">
      <ScrollView contentContainerStyle={styles.scroll}>
        <Row label="Network" value={online ? "Online" : "Offline (degraded)"} />
        <Row label="API avg latency" value={avgApi != null ? `${avgApi} ms` : "—"} />
        <Row label="Offline queue" value={String(queue.length)} />
        <Row label="Evidence pending" value={String(evidence.filter((e) => e.client_sync_status === "pending").length)} />
        <Row label="Device trust" value={trust} />
        <Row label="Realtime events" value={String(events.length)} />
        <Row label="Cold boot" value={getStartupMs() != null ? `${getStartupMs()} ms` : "—"} />
        <Row label="Memory" value={sampleMemoryPlaceholder().note} />
        <Row label="App version" value={Application.nativeApplicationVersion ?? "1.0.0"} />
        <Row label="Build" value={Application.nativeBuildVersion ?? "—"} />
        <Row label="EAS project" value="5aa01d79-7ce7-4c8c-9583-a4a2639848ca" />
        <Row label="Environment" value={String(extra.appEnv ?? process.env.EXPO_PUBLIC_APP_ENV ?? "dev")} />
        <Row label="Sentry ready" value={CrashReporting.isSentryReady() ? "yes" : "placeholder"} />

        <Pressable style={styles.btn} onPress={() => void refresh()}>
          <Text style={styles.btnText}>Refresh realtime</Text>
        </Pressable>
        <Pressable style={styles.btnSecondary} onPress={() => disable()}>
          <Text style={styles.btnText}>Exit QA mode</Text>
        </Pressable>

        <Text style={styles.section}>Operational simulations</Text>
        {listSimulations().map((s) => (
          <Pressable
            key={s.type}
            style={styles.simBtn}
            disabled={simBusy === s.type}
            onPress={async () => {
              setSimBusy(s.type);
              try {
                await runOperationalSimulation(s.type);
              } finally {
                setSimBusy(null);
              }
            }}
          >
            {simBusy === s.type ? (
              <ActivityIndicator color="#fff" />
            ) : (
              <Text style={styles.simText}>{s.label}</Text>
            )}
          </Pressable>
        ))}

        <Text style={styles.section}>Recent metrics</Text>
        {metrics.map((m) => (
          <Text key={`${m.at}-${m.label}`} style={styles.metric}>
            {m.kind} · {m.label} · {m.durationMs}ms
          </Text>
        ))}
      </ScrollView>
    </ScreenShell>
  );
}

function Row({ label, value }: { label: string; value: string }) {
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  scroll: { paddingBottom: 40 },
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    paddingVertical: 10,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: "#334155",
  },
  label: { color: "#94a3b8", fontSize: 12 },
  value: { color: "#e2e8f0", fontSize: 12, fontWeight: "600", maxWidth: "55%", textAlign: "right" },
  muted: { color: "#94a3b8" },
  section: { color: "#38bdf8", fontWeight: "700", marginTop: 20, marginBottom: 8 },
  btn: { backgroundColor: "#0ea5e9", padding: 12, borderRadius: 8, marginTop: 12, alignItems: "center" },
  btnSecondary: { backgroundColor: "#475569", padding: 12, borderRadius: 8, marginTop: 8, alignItems: "center" },
  btnText: { color: "#fff", fontWeight: "600" },
  simBtn: { backgroundColor: "#1e3a5f", padding: 12, borderRadius: 8, marginTop: 6 },
  simText: { color: "#e2e8f0", fontSize: 13 },
  metric: { color: "#64748b", fontSize: 11, marginTop: 4 },
});
