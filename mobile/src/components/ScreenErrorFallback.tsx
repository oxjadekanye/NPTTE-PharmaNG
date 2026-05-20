import { Pressable, StyleSheet, Text, View } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

type Props = {
  message?: string;
  onRetry?: () => void;
};

export function ScreenErrorFallback({ message, onRetry }: Props) {
  return (
    <View style={styles.wrap}>
      <Text style={styles.title}>Something went wrong</Text>
      <Text style={styles.body}>
        {message ?? "An unexpected error occurred. Your session and offline queue are preserved."}
      </Text>
      {onRetry ? (
        <Pressable style={styles.btn} onPress={onRetry}>
          <Text style={styles.btnText}>Try again</Text>
        </Pressable>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    flex: 1,
    justifyContent: "center",
    padding: 24,
    backgroundColor: NPTTEBrand.colors.sovereign.bg,
  },
  title: { color: "#f8fafc", fontSize: 18, fontWeight: "700", marginBottom: 8 },
  body: { color: "#94a3b8", fontSize: 14, lineHeight: 20 },
  btn: {
    marginTop: 20,
    backgroundColor: NPTTEBrand.colors.sovereign.accent,
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  btnText: { color: "#0f172a", fontWeight: "700" },
});
