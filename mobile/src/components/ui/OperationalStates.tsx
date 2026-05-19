import { ReactNode } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

type StateProps = {
  title: string;
  message: string;
  actionLabel?: string;
  onAction?: () => void;
  icon?: ReactNode;
};

function StatePanel({ title, message, actionLabel, onAction, tone }: StateProps & { tone: string }) {
  return (
    <View style={[styles.panel, { borderColor: tone }]}>
      <Text style={styles.title}>{title}</Text>
      <Text style={styles.message}>{message}</Text>
      {actionLabel && onAction && (
        <Pressable style={[styles.btn, { backgroundColor: tone }]} onPress={onAction}>
          <Text style={styles.btnText}>{actionLabel}</Text>
        </Pressable>
      )}
    </View>
  );
}

export function EmptyState(props: StateProps) {
  return <StatePanel {...props} tone={NPTTEBrand.colors.sovereign.border} />;
}

export function DegradedNetworkState(props: StateProps) {
  return <StatePanel {...props} tone={NPTTEBrand.colors.alert.warning} />;
}

export function SyncConflictState(props: StateProps) {
  return <StatePanel {...props} tone={NPTTEBrand.colors.alert.danger} />;
}

export function InvestigationLoadingState() {
  return (
    <View style={styles.panel}>
      <Text style={styles.title}>Loading investigation context</Text>
      <Text style={styles.message}>Retrieving case intelligence from national systems…</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  panel: {
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
    borderRadius: NPTTEBrand.radius.md,
    padding: NPTTEBrand.spacing.xl,
    borderWidth: 1,
    marginVertical: NPTTEBrand.spacing.md,
  },
  title: {
    ...NPTTEBrand.typography.h3,
    color: NPTTEBrand.colors.sovereign.text,
  },
  message: {
    ...NPTTEBrand.typography.body,
    color: NPTTEBrand.colors.sovereign.muted,
    marginTop: NPTTEBrand.spacing.sm,
  },
  btn: {
    marginTop: NPTTEBrand.spacing.lg,
    paddingVertical: 12,
    borderRadius: NPTTEBrand.radius.sm,
    alignItems: "center",
  },
  btnText: { color: "#fff", fontWeight: "700" },
});
