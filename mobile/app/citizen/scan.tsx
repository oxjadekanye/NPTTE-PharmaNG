import { StyleSheet, Text } from "react-native";
import { ScanWorkflow } from "@/components/ScanWorkflow";
import { ScreenShell } from "@/components/ScreenShell";

export default function CitizenScan() {
  return (
    <ScreenShell title="Verify product" subtitle="Scan or enter serial — public verification">
      <ScanWorkflow title="Scan medicine" scanType="citizen_verify" actorRole="citizen" />
      <Text style={styles.hint}>
        If verification fails, check mobile data/Wi‑Fi. Citizen verify uses the public API (no staff
        login).
      </Text>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  hint: { color: "#64748b", fontSize: 12, marginTop: 16, lineHeight: 18 },
});
