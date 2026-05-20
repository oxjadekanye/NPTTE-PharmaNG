import { Pressable, StyleSheet, Text, View } from "react-native";

type Props = {
  message: string;
  onRetry: () => void;
  loading?: boolean;
};

export function RetryPanel({ message, onRetry, loading }: Props) {
  return (
    <View style={styles.wrap}>
      <Text style={styles.msg}>{message}</Text>
      <Pressable style={styles.btn} onPress={onRetry} disabled={loading}>
        <Text style={styles.btnText}>{loading ? "Retrying…" : "Retry"}</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { padding: 16, backgroundColor: "#1e293b", borderRadius: 10, marginVertical: 8 },
  msg: { color: "#94a3b8", fontSize: 13, marginBottom: 10 },
  btn: { backgroundColor: "#0ea5e9", padding: 10, borderRadius: 8, alignItems: "center" },
  btnText: { color: "#fff", fontWeight: "600" },
});
