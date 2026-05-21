import { ReactNode } from "react";
import {
  Modal,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
  ActivityIndicator,
} from "react-native";
import { NPTTEBrand } from "@/theme/branding";

export function DetailRow({ label, value }: { label: string; value: string }) {
  if (!value || value === "—") return null;
  return (
    <View style={styles.row}>
      <Text style={styles.label}>{label}</Text>
      <Text style={styles.value}>{value}</Text>
    </View>
  );
}

export function DetailSheet({
  visible,
  title,
  subtitle,
  onClose,
  loading,
  error,
  children,
}: {
  visible: boolean;
  title: string;
  subtitle?: string;
  onClose: () => void;
  loading?: boolean;
  error?: string | null;
  children: ReactNode;
}) {
  return (
    <Modal visible={visible} animationType="slide" transparent onRequestClose={onClose}>
      <Pressable style={styles.backdrop} onPress={onClose}>
        <Pressable style={styles.sheet} onPress={(e) => e.stopPropagation()}>
          <View style={styles.handle} />
          <Text style={styles.title}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
          {loading ? (
            <View style={styles.center}>
              <ActivityIndicator color={NPTTEBrand.colors.sovereign.accent} />
              <Text style={styles.loadingText}>Loading details…</Text>
            </View>
          ) : error ? (
            <Text style={styles.error}>{error}</Text>
          ) : (
            <ScrollView style={styles.scroll} showsVerticalScrollIndicator={false}>
              {children}
            </ScrollView>
          )}
          <Pressable style={styles.closeBtn} onPress={onClose} accessibilityRole="button">
            <Text style={styles.closeText}>Close</Text>
          </Pressable>
        </Pressable>
      </Pressable>
    </Modal>
  );
}

const styles = StyleSheet.create({
  backdrop: {
    flex: 1,
    backgroundColor: "rgba(2, 6, 23, 0.85)",
    justifyContent: "flex-end",
  },
  sheet: {
    maxHeight: "88%",
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
    borderTopLeftRadius: 16,
    borderTopRightRadius: 16,
    padding: 20,
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
  },
  handle: {
    alignSelf: "center",
    width: 40,
    height: 4,
    borderRadius: 2,
    backgroundColor: "#475569",
    marginBottom: 12,
  },
  title: { color: "#f8fafc", fontSize: 18, fontWeight: "700" },
  subtitle: { color: "#94a3b8", fontSize: 12, marginTop: 4, marginBottom: 12 },
  scroll: { marginVertical: 8 },
  row: { marginBottom: 12 },
  label: { color: "#64748b", fontSize: 11, fontWeight: "600", marginBottom: 4 },
  value: { color: "#e2e8f0", fontSize: 14, lineHeight: 20 },
  center: { alignItems: "center", paddingVertical: 24 },
  loadingText: { color: "#94a3b8", marginTop: 8, fontSize: 12 },
  error: { color: "#fbbf24", marginVertical: 12, fontSize: 13 },
  closeBtn: {
    marginTop: 8,
    backgroundColor: "#1e293b",
    paddingVertical: 12,
    borderRadius: 8,
    alignItems: "center",
  },
  closeText: { color: "#f8fafc", fontWeight: "600" },
});
