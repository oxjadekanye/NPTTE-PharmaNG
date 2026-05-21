import { ReactNode } from "react";
import { StyleSheet, Text, View, type ViewStyle } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

export type LoginSectionVariant = "default" | "credentials" | "action" | "warning" | "error" | "info";

type Props = {
  title: string;
  subtitle?: string;
  variant?: LoginSectionVariant;
  children: ReactNode;
  style?: ViewStyle;
};

const VARIANT_STYLES: Record<
  LoginSectionVariant,
  { border: string; background: string; accent: string; titleColor: string }
> = {
  default: {
    border: NPTTEBrand.colors.sovereign.border,
    background: NPTTEBrand.colors.sovereign.surface,
    accent: NPTTEBrand.colors.sovereign.accent,
    titleColor: NPTTEBrand.colors.sovereign.text,
  },
  credentials: {
    border: "#38bdf8",
    background: "#0c4a6e22",
    accent: "#38bdf8",
    titleColor: "#e0f2fe",
  },
  action: {
    border: NPTTEBrand.colors.sovereign.accentStrong,
    background: "#0284c722",
    accent: NPTTEBrand.colors.sovereign.accentStrong,
    titleColor: "#f0f9ff",
  },
  warning: {
    border: NPTTEBrand.colors.alert.warning,
    background: "#42200688",
    accent: NPTTEBrand.colors.alert.warning,
    titleColor: "#fef3c7",
  },
  error: {
    border: NPTTEBrand.colors.alert.danger,
    background: NPTTEBrand.colors.alert.dangerSurface + "66",
    accent: NPTTEBrand.colors.alert.danger,
    titleColor: "#fecaca",
  },
  info: {
    border: "#64748b",
    background: NPTTEBrand.colors.sovereign.elevated,
    accent: NPTTEBrand.colors.sovereign.muted,
    titleColor: "#cbd5e1",
  },
};

/** Highlighted panel for login screen sections — keeps layout modular per screen. */
export function LoginSection({ title, subtitle, variant = "default", children, style }: Props) {
  const palette = VARIANT_STYLES[variant];

  return (
    <View
      style={[
        styles.section,
        {
          borderColor: palette.border,
          backgroundColor: palette.background,
        },
        style,
      ]}
      accessibilityRole="summary"
      accessibilityLabel={title}
    >
      <View style={styles.header}>
        <View style={[styles.accentBar, { backgroundColor: palette.accent }]} />
        <View style={styles.headerText}>
          <Text style={[styles.title, { color: palette.titleColor }]}>{title}</Text>
          {subtitle ? <Text style={styles.subtitle}>{subtitle}</Text> : null}
        </View>
      </View>
      <View style={styles.body}>{children}</View>
    </View>
  );
}

const styles = StyleSheet.create({
  section: {
    borderWidth: 2,
    borderRadius: NPTTEBrand.radius.md,
    marginBottom: NPTTEBrand.spacing.lg,
    overflow: "hidden",
  },
  header: {
    flexDirection: "row",
    alignItems: "stretch",
    borderBottomWidth: 1,
    borderBottomColor: NPTTEBrand.colors.sovereign.border,
    backgroundColor: "#00000033",
  },
  accentBar: {
    width: 5,
  },
  headerText: {
    flex: 1,
    paddingVertical: NPTTEBrand.spacing.sm,
    paddingHorizontal: NPTTEBrand.spacing.md,
  },
  title: {
    fontSize: 15,
    fontWeight: "700",
    letterSpacing: 0.3,
  },
  subtitle: {
    color: NPTTEBrand.colors.sovereign.muted,
    fontSize: 12,
    marginTop: 2,
    lineHeight: 16,
  },
  body: {
    padding: NPTTEBrand.spacing.md,
    gap: NPTTEBrand.spacing.sm,
  },
});
