import { router } from "expo-router";
import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { login, fetchPermissions } from "@/services/auth";
import { registerTrustedDevice, sendDeviceHeartbeat } from "@/services/device-trust";
import { isBiometricHardwareAvailable } from "@/services/biometric";
import { initPushOrchestration } from "@/services/push-orchestration";
import { mobileHomePath, resolveMobileRole } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";

export default function LoginScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const hydrate = useAuthStore((s) => s.hydrate);
  const sessionExpired = useAuthStore((s) => s.sessionExpired);

  const onLogin = async () => {
    setLoading(true);
    setError(null);
    try {
      await login({ username, password });
      await hydrate();
      const perms = await fetchPermissions();
      const role = resolveMobileRole(perms.role_code, perms.is_regulator);
      if (!role) {
        throw new Error("No mobile role assigned for this account");
      }
      const bio = await isBiometricHardwareAvailable();
      await registerTrustedDevice(bio);
      await initPushOrchestration(role === "executive" ? "executive" : "officer_tasks");
      void sendDeviceHeartbeat();
      router.replace(mobileHomePath(role));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Login failed");
    } finally {
      setLoading(false);
    }
  };

  return (
    <ScreenShell title="Staff login" subtitle="JWT authentication via existing NPTTE API">
      <TextInput
        style={styles.input}
        placeholder="Username"
        placeholderTextColor="#64748b"
        autoCapitalize="none"
        value={username}
        onChangeText={setUsername}
      />
      <TextInput
        style={styles.input}
        placeholder="Password"
        placeholderTextColor="#64748b"
        secureTextEntry
        value={password}
        onChangeText={setPassword}
      />
      {sessionExpired && (
        <Text style={styles.warn}>Your session expired. Please sign in again.</Text>
      )}
      {error && <Text style={styles.error}>{error}</Text>}
      <Pressable style={styles.btn} onPress={() => void onLogin()} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Sign in</Text>}
      </Pressable>
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
    backgroundColor: "#0f172a",
  },
  btn: {
    backgroundColor: "#0284c7",
    padding: 14,
    borderRadius: 8,
    alignItems: "center",
    marginTop: 8,
  },
  btnText: { color: "#fff", fontWeight: "600" },
  error: { color: "#fca5a5", marginBottom: 8 },
  warn: { color: "#fbbf24", marginBottom: 8, fontSize: 13 },
});
