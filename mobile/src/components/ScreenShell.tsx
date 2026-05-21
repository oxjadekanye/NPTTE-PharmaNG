import { ReactNode } from "react";
import { ScrollView, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { OfflineStatusBar } from "@/components/OfflineStatusBar";
import { NPTTEBrand } from "@/theme/branding";

export function ScreenShell({
  title,
  subtitle,
  children,
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
}) {
  return (
    <SafeAreaView style={styles.safe} edges={["top", "left", "right"]}>
      <OfflineStatusBar />
      <ScrollView
        contentContainerStyle={styles.scroll}
        showsVerticalScrollIndicator={false}
        keyboardShouldPersistTaps="handled"
        nestedScrollEnabled
      >
        <Text style={styles.title}>{title}</Text>
        {subtitle ? <Text style={styles.sub}>{subtitle}</Text> : null}
        <View style={styles.body}>{children}</View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: NPTTEBrand.colors.sovereign.bg },
  scroll: {
    padding: NPTTEBrand.spacing.lg,
    paddingBottom: NPTTEBrand.spacing.section,
  },
  title: {
    ...NPTTEBrand.typography.h2,
    color: NPTTEBrand.colors.sovereign.text,
  },
  sub: {
    ...NPTTEBrand.typography.caption,
    color: NPTTEBrand.colors.sovereign.muted,
    marginTop: NPTTEBrand.spacing.xs,
    marginBottom: NPTTEBrand.spacing.lg,
    lineHeight: 18,
  },
  body: { marginTop: NPTTEBrand.spacing.sm },
});
