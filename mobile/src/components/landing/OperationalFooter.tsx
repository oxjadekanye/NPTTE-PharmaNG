import { useEffect, useRef } from "react";
import { Animated, Dimensions, StyleSheet, Text, View } from "react-native";
import { useOperationalTicker } from "@/hooks/useOperationalTicker";
import { LANDING_COLORS } from "@/components/landing/landing-styles";

const { width: SCREEN_W } = Dimensions.get("window");
const isNarrow = SCREEN_W < 360;

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
    <View style={styles.footer} pointerEvents="none">
      <Text style={styles.footerTitle}>National operations — live feed</Text>
      <View style={styles.grid}>
        <Metric label="Verifications today" value={snapshot.verificationsToday} fade={fade} />
        <Metric label="Active recalls" value={snapshot.activeRecalls} fade={fade} />
        <Metric label="Enforcement actions" value={snapshot.enforcementActions} fade={fade} />
        <Metric label="System uptime" value={snapshot.systemUptime} fade={fade} />
      </View>
    </View>
  );
}

const styles = StyleSheet.create({
  footer: {
    borderTopWidth: 1,
    borderTopColor: "#33415588",
    paddingTop: isNarrow ? 14 : 20,
    marginTop: isNarrow ? 12 : 20,
    paddingBottom: 4,
  },
  footerTitle: {
    color: "#94a3b8",
    fontSize: 11,
    letterSpacing: 1.4,
    textTransform: "uppercase",
    marginBottom: 14,
    textAlign: "center",
    fontWeight: "700",
  },
  grid: {
    flexDirection: "row",
    flexWrap: "wrap",
    justifyContent: "space-between",
    rowGap: 14,
    columnGap: 8,
  },
  metric: {
    width: isNarrow ? "48%" : "47%",
    alignItems: "center",
    paddingVertical: 8,
    paddingHorizontal: 4,
    borderRadius: 10,
    backgroundColor: "rgba(15, 23, 42, 0.65)",
    borderWidth: 1,
    borderColor: "#33415555",
  },
  metricValue: {
    color: LANDING_COLORS.badgeGreen,
    fontSize: isNarrow ? 17 : 20,
    fontWeight: "800",
    letterSpacing: -0.5,
  },
  metricLabel: {
    color: "#cbd5e1",
    fontSize: isNarrow ? 9 : 10,
    marginTop: 5,
    textAlign: "center",
    lineHeight: 14,
    fontWeight: "600",
  },
});
