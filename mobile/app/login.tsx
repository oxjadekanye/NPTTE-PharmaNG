import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { PasswordInput } from "@/components/PasswordInput";
import { ScreenShell } from "@/components/ScreenShell";
import {
  login,
  fetchPermissions,
  fetchProfile,
  LOGIN_VALIDATION_HINT,
} from "@/services/auth";
import { registerTrustedDevice, sendDeviceHeartbeat } from "@/services/device-trust";
import { isBiometricHardwareAvailable } from "@/services/biometric";
import { initPushOrchestration } from "@/services/push-orchestration";
import { mobileHomePath, resolveMobileRole } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";
import { NPTTEBrand } from "@/theme/branding";

const DEMO_ACCOUNTS = [
  { user: "nptte_admin", password: "NptteAdmin2026!" },
  { user: "demo_pharmacy_admin", password: "DemoPharmacy2026!" },
  { user: "demo_patient", password: "DemoPatient2026!" },
] as const;

export default function LoginScreen() {
  const setStaffLoginIntent = useLandingIntent((s) => s.setStaffLoginIntent);

  useEffect(() => {
    return () => setStaffLoginIntent(false);
  }, [setStaffLoginIntent]);

  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const sessionExpired = useAuthStore((s) => s.sessionExpired);

  const onLogin = async () => {
    const trimmedUser = username.trim();
    const trimmedPassword = password.trim();
    if (!trimmedUser || !trimmedPassword) {
      setError("Enter username and password");
      return;
    }
    setLoading(true);
    setError(null);
    try {
      await login({ username: trimmedUser, password: trimmedPassword });
      const [profile, perms] = await Promise.all([fetchProfile(), fetchPermissions()]);
      const role = resolveMobileRole(perms.role_code, perms.is_regulator);
      if (!role) {
        throw new Error(
          `No mobile role for account (${perms.role_code ?? "unknown"}). Contact your administrator.`
        );
      }
      useLandingIntent.getState().clearPublicFlow();
      useLandingIntent.getState().setStaffLoginIntent(false);
      useNavigationStore.getState().clearNavigationDedupe();
      useAuthStore.setState({
        profile,
        permissions: perms,
        mobileRole: role,
        loading: false,
        sessionExpired: false,
      });
      useNavigationStore.getState().replaceWhenReady(mobileHomePath(role));
      const bio = await isBiometricHardwareAvailable();
      const trust = await registerTrustedDevice(bio);
      if (!trust.success) {
        console.warn("Device trust registration skipped:", trust.message);
      }
      const pushChannel =
        role === "executive" ? "executive" : role === "regulator" ? "officer_tasks" : "officer_tasks";
      await initPushOrchestration(pushChannel);
      void sendDeviceHeartbeat();
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Login failed";
      if (msg.includes("abort") || msg.includes("network") || msg.includes("Failed to fetch")) {
        setError("Cannot reach NPTTE API. Check network or try again on Wi‑Fi/LTE.");
      } else if (/no active account|inactive|invalid|password|credentials|401|403/i.test(msg)) {
        setError(LOGIN_VALIDATION_HINT);
      } else {
        setError(msg);
      }
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
        <Text style={styles.hintTitle}>Demo accounts (exact — case sensitive)</Text>
        {DEMO_ACCOUNTS.map((row) => (
          <View key={row.user} style={styles.demoRow}>
            <Text style={styles.hintUser}>Username: {row.user}</Text>
            <Text style={styles.hintPass}>Password: {row.password}</Text>
          </View>
        ))}
        <Text style={styles.hintSub}>Seed on Render: python manage.py seed_demo_data</Text>
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
  error: { color: "#fca5a5", marginBottom: 8, lineHeight: 18 },
  warn: { color: "#fbbf24", marginBottom: 8, fontSize: 13 },
  hint: {
    marginTop: NPTTEBrand.spacing.xl,
    padding: NPTTEBrand.spacing.md,
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
    borderRadius: NPTTEBrand.radius.sm,
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
  },
  hintTitle: { color: NPTTEBrand.colors.sovereign.muted, fontSize: 11, marginBottom: 8 },
  demoRow: { marginBottom: 8 },
  hintUser: { color: "#e2e8f0", fontSize: 12, fontWeight: "600" },
  hintPass: { color: NPTTEBrand.colors.sovereign.muted, fontSize: 12, marginTop: 2 },
  hintSub: { color: NPTTEBrand.colors.sovereign.muted, fontSize: 10, marginTop: 8 },
});
