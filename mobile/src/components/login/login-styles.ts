import { StyleSheet } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

export const loginFieldStyles = StyleSheet.create({
  label: {
    color: NPTTEBrand.colors.sovereign.muted,
    fontSize: 12,
    fontWeight: "600",
    marginBottom: 4,
    textTransform: "uppercase",
    letterSpacing: 0.5,
  },
  input: {
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
    borderRadius: NPTTEBrand.radius.sm,
    padding: 12,
    color: NPTTEBrand.colors.sovereign.text,
    backgroundColor: NPTTEBrand.colors.sovereign.bg,
    minHeight: 48,
  },
  btn: {
    backgroundColor: NPTTEBrand.colors.sovereign.accentStrong,
    padding: 14,
    borderRadius: NPTTEBrand.radius.sm,
    alignItems: "center",
    minHeight: 48,
    justifyContent: "center",
  },
  btnText: { color: "#fff", fontWeight: "700", fontSize: 16 },
  message: { lineHeight: 18, fontSize: 13 },
  demoRow: {
    padding: NPTTEBrand.spacing.sm,
    borderRadius: NPTTEBrand.radius.sm,
    backgroundColor: NPTTEBrand.colors.sovereign.bg,
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
    marginBottom: NPTTEBrand.spacing.sm,
  },
  hintUser: { color: "#e2e8f0", fontSize: 13, fontWeight: "700" },
  hintPass: { color: NPTTEBrand.colors.sovereign.muted, fontSize: 12, marginTop: 4 },
  hintSub: { color: NPTTEBrand.colors.sovereign.muted, fontSize: 10, marginTop: NPTTEBrand.spacing.sm },
});
