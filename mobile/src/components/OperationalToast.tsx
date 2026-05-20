import { Pressable, StyleSheet, Text, View } from "react-native";
import { useOperationalToast } from "@/store/operational-toast-store";

const COLORS = {
  info: "#0ea5e9",
  success: "#22c55e",
  warning: "#f59e0b",
  error: "#ef4444",
} as const;

export function OperationalToast() {
  const current = useOperationalToast((s) => s.current);
  const dismiss = useOperationalToast((s) => s.dismiss);
  if (!current) return null;

  return (
    <Pressable style={[styles.wrap, { borderLeftColor: COLORS[current.kind] }]} onPress={dismiss}>
      <Text style={styles.text}>{current.text}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  wrap: {
    position: "absolute",
    left: 16,
    right: 16,
    bottom: 48,
    zIndex: 9999,
    backgroundColor: "#1e293b",
    borderLeftWidth: 4,
    padding: 14,
    borderRadius: 10,
    elevation: 8,
  },
  text: { color: "#f1f5f9", fontSize: 13 },
});
