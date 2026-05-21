import { router } from "expo-router";
import { Pressable, StyleSheet, Text } from "react-native";
import { bootLog } from "@/services/boot-diagnostics";

type Props = {
  href: string;
  label: string;
};

/** Imperative navigation — Link/asChild is unreliable on Android production builds. */
export function MenuButton({ href, label }: Props) {
  return (
    <Pressable
      style={({ pressed }) => [styles.btn, pressed && styles.pressed]}
      accessibilityRole="button"
      onPress={() => {
        bootLog("navigation", `menu push → ${href}`);
        router.push(href as never);
      }}
    >
      <Text style={styles.text}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    padding: 14,
    borderRadius: 10,
    marginBottom: 10,
  },
  pressed: { opacity: 0.85, backgroundColor: "#334155" },
  text: { color: "#e2e8f0", fontSize: 15 },
});
