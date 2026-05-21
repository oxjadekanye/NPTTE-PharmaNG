import { Pressable, StyleSheet, Text } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import {
  CITIZEN_ROUTES,
  pushCitizenRoute,
  returnToLanding,
} from "@/services/citizen-navigation";

export default function CitizenHome() {
  return (
    <ScreenShell title="Citizen" subtitle="Verify medicines without an account">
      <CitizenAction
        label="Scan or verify serial"
        onPress={() => pushCitizenRoute(CITIZEN_ROUTES.scan)}
      />
      <CitizenAction
        label="Manual serial lookup"
        onPress={() => pushCitizenRoute(CITIZEN_ROUTES.manual)}
      />
      <CitizenAction
        label="Recall alerts"
        onPress={() => pushCitizenRoute(CITIZEN_ROUTES.recalls)}
      />
      <CitizenAction
        label="Report counterfeit"
        onPress={() => pushCitizenRoute(CITIZEN_ROUTES.report)}
      />
      <Pressable style={styles.back} onPress={returnToLanding}>
        <Text style={styles.link}>← Back to home</Text>
      </Pressable>
    </ScreenShell>
  );
}

function CitizenAction({ label, onPress }: { label: string; onPress: () => void }) {
  return (
    <Pressable
      style={({ pressed }) => [styles.btn, pressed && styles.pressed]}
      accessibilityRole="button"
      onPress={onPress}
    >
      <Text style={styles.text}>{label}</Text>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  btn: {
    backgroundColor: "#1e293b",
    borderWidth: 1,
    borderColor: "#334155",
    padding: 14,
    borderRadius: 10,
    marginBottom: 10,
  },
  pressed: { opacity: 0.85, backgroundColor: "#334155" },
  text: { color: "#e2e8f0", fontSize: 15 },
  back: { marginTop: 16, padding: 12 },
  link: { color: "#38bdf8", textAlign: "center", fontSize: 15 },
});
