import { useState } from "react";
import { Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { EvidenceCapture } from "@/components/EvidenceCapture";
import { mobileCopilot } from "@/services/mobile-ai";

export default function CustomsHold() {
  const [manifest, setManifest] = useState("");
  const [recommendation, setRecommendation] = useState<string | null>(null);

  const recommend = async () => {
    const res = await mobileCopilot({
      prompt_mode: "operational_recommendations",
      user_question: `Suspicious consignment manifest ${manifest}. Recommend hold or release.`,
    });
    if (res.success && res.data) {
      setRecommendation(String(res.data.summary));
    }
  };

  return (
    <ScreenShell title="Hold consignment" subtitle="Suspicious import workflow">
      <TextInput
        style={styles.input}
        placeholder="Manifest / shipment ref"
        placeholderTextColor="#64748b"
        value={manifest}
        onChangeText={setManifest}
      />
      <Pressable style={styles.btn} onPress={() => void recommend()}>
        <Text style={styles.btnText}>Hold / release recommendation (AI)</Text>
      </Pressable>
      {recommendation && <Text style={styles.rec}>{recommendation}</Text>}
      <View style={styles.gap} />
      <EvidenceCapture evidenceType="customs_seizure" serialNumber={manifest} />
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: "#334155",
    borderRadius: 8,
    padding: 12,
    color: "#f1f5f9",
    marginBottom: 12,
  },
  btn: { backgroundColor: "#b45309", padding: 12, borderRadius: 8 },
  btnText: { color: "#fff", textAlign: "center", fontWeight: "600" },
  rec: { color: "#fcd34d", marginTop: 12, fontSize: 12 },
  gap: { height: 16 },
});
