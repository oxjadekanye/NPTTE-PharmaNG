import { router } from "expo-router";
import { Pressable, StyleSheet, Text } from "react-native";
import { MenuButton } from "@/components/MenuButton";
import { ScreenShell } from "@/components/ScreenShell";

export default function CitizenHome() {
  return (
    <ScreenShell title="Citizen" subtitle="Verify medicines without an account">
      <MenuButton href="/citizen/scan" label="Scan or verify serial" />
      <MenuButton href="/citizen/manual" label="Manual serial lookup" />
      <MenuButton href="/citizen/recalls" label="Recall alerts" />
      <MenuButton href="/citizen/report" label="Report counterfeit" />
      <Pressable onPress={() => router.replace("/")}>
        <Text style={styles.link}>← Back to welcome</Text>
      </Pressable>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  link: { color: "#38bdf8", marginTop: 16, textAlign: "center" },
});
