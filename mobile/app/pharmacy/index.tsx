import { router } from "expo-router";
import { Pressable, StyleSheet, Text } from "react-native";
import { MenuButton } from "@/components/MenuButton";
import { ScreenShell } from "@/components/ScreenShell";
import { useAuthStore } from "@/store/auth-store";

export default function PharmacyHome() {
  const signOut = useAuthStore((s) => s.signOut);
  return (
    <ScreenShell title="Pharmacy" subtitle="Receive, dispense, recalls — offline queue enabled">
      <MenuButton href="/pharmacy/receive" label="Receive stock" />
      <MenuButton href="/pharmacy/dispense" label="Dispense product" />
      <MenuButton href="/pharmacy/recalls" label="Acknowledge recalls" />
      <MenuButton href="/offline-queue" label="Offline queue" />
      <Pressable
        onPress={() => {
          void signOut().then(() => router.replace("/"));
        }}
      >
        <Text style={styles.out}>Sign out</Text>
      </Pressable>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  out: { color: "#94a3b8", textAlign: "center", marginTop: 24 },
});
