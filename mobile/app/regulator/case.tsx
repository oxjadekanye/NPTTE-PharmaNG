import { Text } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";

export default function RegulatorCase() {
  return (
    <ScreenShell title="Enforcement case" subtitle="Create via web; open investigation room on mobile web">
      <Text style={{ color: "#94a3b8" }}>
        New cases are created through the enforcement API on the command platform. Field officers can
        add investigation notes via the investigation room once a case ID is assigned.
      </Text>
    </ScreenShell>
  );
}
