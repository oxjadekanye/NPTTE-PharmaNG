import { Text } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";

export default function PharmacyRecalls() {
  return (
    <ScreenShell title="Recalls" subtitle="Acknowledge national recalls (web workflow link)">
      <Text style={{ color: "#94a3b8" }}>
        Recall acknowledgement uses the same national alert APIs. Full workflow remains on the web
        command platform; mobile shows alerts from scan outcomes.
      </Text>
    </ScreenShell>
  );
}
