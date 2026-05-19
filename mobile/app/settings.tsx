import { useEffect, useState } from "react";
import { Pressable, StyleSheet, Switch, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import {
  getBiometricEnabled,
  isBiometricHardwareAvailable,
  setBiometricEnabled,
} from "@/services/biometric";
import { loadPushPreferences, savePushPreferences, type PushPreferences } from "@/services/push-orchestration";

export default function SettingsScreen() {
  const [bio, setBio] = useState(false);
  const [bioAvailable, setBioAvailable] = useState(false);
  const [prefs, setPrefs] = useState<PushPreferences | null>(null);

  useEffect(() => {
    void (async () => {
      setBio(await getBiometricEnabled());
      setBioAvailable(await isBiometricHardwareAvailable());
      setPrefs(await loadPushPreferences());
    })();
  }, []);

  const togglePref = (key: keyof PushPreferences) => {
    if (!prefs) return;
    const next = { ...prefs, [key]: !prefs[key] };
    setPrefs(next);
    void savePushPreferences(next);
  };

  return (
    <ScreenShell title="Settings" subtitle="Security & notifications">
      <View style={styles.row}>
        <Text style={styles.label}>Biometric unlock</Text>
        <Switch
          value={bio}
          disabled={!bioAvailable}
          onValueChange={(v) => {
            setBio(v);
            void setBiometricEnabled(v);
          }}
        />
      </View>
      {!bioAvailable && <Text style={styles.muted}>Biometrics not available on this device</Text>}
      {prefs && (
        <>
          <Text style={styles.section}>Notification preferences</Text>
          {(Object.keys(prefs) as (keyof PushPreferences)[]).map((key) => (
            <View key={key} style={styles.row}>
              <Text style={styles.label}>{key.replace(/_/g, " ")}</Text>
              <Switch value={prefs[key]} onValueChange={() => togglePref(key)} />
            </View>
          ))}
        </>
      )}
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  row: {
    flexDirection: "row",
    justifyContent: "space-between",
    alignItems: "center",
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
  },
  label: { color: "#e2e8f0", textTransform: "capitalize" },
  muted: { color: "#64748b", fontSize: 12, marginBottom: 12 },
  section: { color: "#38bdf8", marginTop: 16, marginBottom: 8, fontWeight: "600" },
});
