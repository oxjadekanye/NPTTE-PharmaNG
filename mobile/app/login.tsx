import { router } from "expo-router";
import { useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { PasswordInput } from "@/components/PasswordInput";
import { ScreenShell } from "@/components/ScreenShell";
import { login, fetchPermissions, parseLoginError } from "@/services/auth";
import { registerTrustedDevice, sendDeviceHeartbeat } from "@/services/device-trust";
import { isBiometricHardwareAvailable } from "@/services/biometric";
import { initPushOrchestration } from "@/services/push-orchestration";
import { mobileHomePath, resolveMobileRole } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";
import { NPTTEBrand } from "@/theme/branding";

export default function LoginScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const hydrate = useAuthStore((s) => s.hydrate);
  const sessionExpired = useAuthStore((s) => s.sessionExpired);

  const onLogin = async () => {
    const trimmedUser = username.trim();
    if (!trimmedUser || !password) {
      setError("Enter username and password");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await login({ username: trimmedUser, password });
      await hydrate();
      const perms = await fetchPermissions();
      const role = resolveMobileRole(perms.role_code, perms.is_regulator);
      if (!role) {
        throw new Error(
          `No mobile role for account (${perms.role_code ?? "unknown"}). Contact your administrator.`
        );
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
    <ScreenShell title="Staff login" subtitle="National field & pharmacy access">
      <TextInput
        style={styles.input}
        placeholder="Username"
        placeholderTextColor={NPTTEBrand.colors.sovereign.muted}
        autoCapitalize="none"
        autoCorrect={false}
        value={username}
        onChangeText={setUsername}
        editable={!loading}
      />
      <PasswordInput
        placeholder="Password"
        value={password}
        onChangeText={setPassword}
        editable={!loading}
        onSubmitEditing={() => void onLogin()}
      />
      {sessionExpired && (
        <Text style={styles.warn}>Your session expired. Please sign in again.</Text>
      )}
      {error && <Text style={styles.error}>{error}</Text>}
      <Pressable style={styles.btn} onPress={() => void onLogin()} disabled={loading}>
        {loading ? <ActivityIndicator color="#fff" /> : <Text style={styles.btnText}>Sign in</Text>}
      </Pressable>
      <View style={styles.hint}>
        <Text style={styles.hintTitle}>Demo accounts</Text>
        <Text style={styles.hintText}>Pharmacy: demo_pharmacy_admin</Text>
        <Text style={styles.hintText}>Patient (citizen app): demo_patient</Text>
      </View>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  input: {
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
    borderRadius: NPTTEBrand.radius.sm,
    padding: 12,
    color: NPTTEBrand.colors.sovereign.text,
    marginBottom: NPTTEBrand.spacing.md,
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
  },
  btn: {
    backgroundColor: NPTTEBrand.colors.sovereign.accentStrong,
    padding: 14,
    borderRadius: NPTTEBrand.radius.sm,
    alignItems: "center",
    marginTop: NPTTEBrand.spacing.sm,
  },
  btnText: { color: "#fff", fontWeight: "600" },
  error: { color: "#fca5a5", marginBottom: 8 },
  warn: { color: "#fbbf24", marginBottom: 8, fontSize: 13 },
  hint: {
    marginTop: NPTTEBrand.spacing.xl,
    padding: NPTTEBrand.spacing.md,
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
    borderRadius: NPTTEBrand.radius.sm,
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
  },
  hintTitle: { color: NPTTEBrand.colors.sovereign.muted, fontSize: 11, marginBottom: 6 },
  hintText: { color: NPTTEBrand.colors.sovereign.muted, fontSize: 12 },
});
