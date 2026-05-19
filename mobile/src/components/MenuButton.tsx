import { Link } from "expo-router";
import { Pressable, StyleSheet, Text } from "react-native";

export function MenuButton({ href, label }: { href: string; label: string }) {
  return (
    <Link href={href} asChild>
      <Pressable style={styles.btn}>
        <Text style={styles.text}>{label}</Text>
      </Pressable>
    </Link>
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
  text: { color: "#e2e8f0", fontSize: 15 },
});
