import { Pressable, StyleSheet, Text } from "react-native";
import { MenuButton } from "@/components/MenuButton";
import { ScreenShell } from "@/components/ScreenShell";
import { useAuthStore } from "@/store/auth-store";
import { useNavigationStore } from "@/store/navigation-store";

export default function RegulatorHome() {
  const signOut = useAuthStore((s) => s.signOut);
  return (
    <ScreenShell title="Field regulator" subtitle="Inspections, enforcement, tasks">
      <MenuButton href="/regulator/inspect" label="Field inspection scan" />
      <MenuButton href="/regulator/checklist" label="Inspection checklist" />
      <MenuButton href="/regulator/evidence" label="Upload evidence (placeholder)" />
      <MenuButton href="/regulator/note" label="Draft enforcement note" />
      <MenuButton href="/regulator/case" label="Open / create case" />
      <MenuButton href="/offline-queue" label="Offline queue" />
      <MenuButton href="/sync-health" label="Sync health" />
      <MenuButton href="/field-activity" label="Field activity log" />
      <MenuButton href="/settings" label="Settings & biometrics" />
      <Pressable
        onPress={() =>
          void signOut().then(() => useNavigationStore.getState().replaceWhenReady("/"))
        }
      >
        <Text style={styles.out}>Sign out</Text>
      </Pressable>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  out: { color: "#94a3b8", textAlign: "center", marginTop: 24 },
});
