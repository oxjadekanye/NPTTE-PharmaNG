import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { authenticateWithBiometrics, getBiometricEnabled } from "@/services/biometric";
import { getAccessToken } from "@/services/auth-storage";

export function BiometricGate({ children }: { children: React.ReactNode }) {
  const [checking, setChecking] = useState(true);
  const [unlocked, setUnlocked] = useState(false);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    (async () => {
      const token = await getAccessToken();
      const enabled = await getBiometricEnabled();
      if (!token || !enabled) {
        setUnlocked(true);
        setChecking(false);
        return;
      }
      const ok = await authenticateWithBiometrics();
      setUnlocked(ok);
      setFailed(!ok);
      setChecking(false);
    })();
  }, []);

  if (checking) {
    return (
      <View style={styles.center}>
        <ActivityIndicator color="#38bdf8" />
      </View>
    );
  }

  if (unlocked) return <>{children}</>;

  return (
    <View style={styles.center}>
      <Text style={styles.title}>Biometric lock</Text>
      {failed && <Text style={styles.error}>Authentication failed</Text>}
      <Pressable
        style={styles.btn}
        onPress={async () => {
          const ok = await authenticateWithBiometrics();
          if (ok) setUnlocked(true);
          else setFailed(true);
        }}
      >
        <Text style={styles.btnText}>Unlock with biometrics</Text>
      </Pressable>
      <Pressable onPress={() => router.replace("/login")}>
        <Text style={styles.link}>Use password instead</Text>
      </Pressable>
    </View>
  );
}

const styles = StyleSheet.create({
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#020617", padding: 24 },
  title: { color: "#f8fafc", fontSize: 18, marginBottom: 12 },
  error: { color: "#fca5a5", marginBottom: 8 },
  btn: { backgroundColor: "#0284c7", padding: 14, borderRadius: 8, marginBottom: 12 },
  btnText: { color: "#fff", fontWeight: "600" },
  link: { color: "#38bdf8" },
});
