import { useEffect, useRef } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { useOperationalTicker } from "@/hooks/useOperationalTicker";

function Metric({ label, value, fade }: { label: string; value: string; fade: Animated.Value }) {
  return (
    <Animated.View style={[styles.metric, { opacity: fade }]}>
      <Text style={styles.metricValue}>{value}</Text>
      <Text style={styles.metricLabel}>{label}</Text>
    </Animated.View>
  );
}

export function OperationalFooter() {
  const snapshot = useOperationalTicker(3500);
  const fade = useRef(new Animated.Value(1)).current;

  useEffect(() => {
    fade.setValue(0);
    Animated.timing(fade, { toValue: 1, duration: 420, useNativeDriver: true }).start();
  }, [snapshot, fade]);

  return (
    <View style={styles.footer}>
      <Text style={styles.footerTitle}>National operations — live feed</Text>
      <View style={styles.grid}>
        <Metric label="Verifications today" value={snapshot.verificationsToday} fade={fade} />
        <Metric label="Active recalls" value={snapshot.activeRecalls} fade={fade} />
        <Metric label="Counterfeit alerts" value={snapshot.counterfeitAlerts} fade={fade} />
        <Metric label="Enforcement readiness" value={snapshot.enforcementReadiness} fade={fade} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  footer: {
    borderTopWidth: 1,
    borderTopColor: "#1e293b",
    paddingTop: 16,
    marginTop: 8,
  },
  footerTitle: {
    color: "#64748b",
    fontSize: 10,
    letterSpacing: 1.2,
    textTransform: "uppercase",
    marginBottom: 12,
    textAlign: "center",
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    rowGap: 12,
  },
  metric: { width: "48%", alignItems: "center" },
  metricValue: { color: "#4ade80", fontSize: 18, fontWeight: "700", letterSpacing: -0.5 },
  metricLabel: { color: "#94a3b8", fontSize: 10, marginTop: 4, textAlign: "center", lineHeight: 14 },
});
