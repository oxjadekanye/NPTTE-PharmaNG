import { ReactNode } from "react";
import { StyleSheet, Text, View, type ViewStyle } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

export function OperationalCard({
  title,
  subtitle,
  children,
  variant = "default",
  style,
}: {
  title?: string;
  subtitle?: string;
  children: ReactNode;
  variant?: "default" | "enforcement" | "intelligence";
  style?: ViewStyle;
}) {
  const borderColor =
    variant === "enforcement"
      ? NPTTEBrand.colors.enforcement.border
      : variant === "intelligence"
        ? NPTTEBrand.colors.intelligence.glow
        : NPTTEBrand.colors.sovereign.border;

  return (
    <View style={[styles.card, { borderColor }, style]}>
      {title && <Text style={styles.title}>{title}</Text>}
      {subtitle && <Text style={styles.sub}>{subtitle}</Text>}
      {children}
    </View>
  );
}

const styles = StyleSheet.create({
  card: {
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
    borderRadius: NPTTEBrand.radius.md,
    padding: NPTTEBrand.spacing.lg,
    marginBottom: NPTTEBrand.spacing.md,
    borderWidth: 1,
    ...NPTTEBrand.shadow.card,
  },
  title: {
    ...NPTTEBrand.typography.h3,
    color: NPTTEBrand.colors.sovereign.text,
  },
  sub: {
    ...NPTTEBrand.typography.caption,
    color: NPTTEBrand.colors.sovereign.muted,
    marginTop: NPTTEBrand.spacing.xs,
    marginBottom: NPTTEBrand.spacing.sm,
  },
});
