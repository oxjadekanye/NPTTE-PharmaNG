import { useState } from "react";
import { Pressable, StyleSheet, Text, View } from "react-native";
import { InspectionChecklistEngine } from "@/components/InspectionChecklistEngine";
import { ScreenShell } from "@/components/ScreenShell";
import type { InspectionSectionId } from "@/services/mobile-inspection";

const TABS: { id: InspectionSectionId; label: string }[] = [
  { id: "site", label: "Site" },
  { id: "product", label: "Product" },
  { id: "compliance", label: "Compliance" },
];

export default function RegulatorChecklist() {
  const [activeSection, setActiveSection] = useState<InspectionSectionId>("site");
  const [checks, setChecks] = useState<Record<string, boolean>>({});

  return (
    <ScreenShell title="Inspection checklist" subtitle="Pass/fail sections · compliance score">
      <View style={styles.tabs}>
        {TABS.map((t) => (
          <Pressable
            key={t.id}
            style={[styles.tab, activeSection === t.id && styles.tabActive]}
            onPress={() => setActiveSection(t.id)}
          >
            <Text style={styles.tabText}>{t.label}</Text>
          </Pressable>
        ))}
      </View>
      <InspectionChecklistEngine
        activeSection={activeSection}
        checks={checks}
        onToggle={(key) => setChecks((c) => ({ ...c, [key]: !c[key] }))}
      />
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  tabs: { flexDirection: "row", gap: 8, marginBottom: 12 },
  tab: { padding: 8, borderRadius: 8, backgroundColor: "#1e293b" },
  tabActive: { backgroundColor: "#0284c7" },
  tabText: { color: "#e2e8f0", fontSize: 12, fontWeight: "600" },
});
