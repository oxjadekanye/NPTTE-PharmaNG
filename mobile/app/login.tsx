import { useEffect, useRef, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from "react-native";
import { PasswordInput } from "@/components/PasswordInput";
import { ScreenShell } from "@/components/ScreenShell";
import { login, fetchPermissions, fetchProfile } from "@/services/auth";
import { registerTrustedDevice, sendDeviceHeartbeat } from "@/services/device-trust";
import { isBiometricHardwareAvailable } from "@/services/biometric";
import { initPushOrchestration } from "@/services/push-orchestration";
import { mobileHomePath, resolveMobileRole, type MobileRole } from "@/services/role-routing";
import { useRootMounted } from "@/hooks/useRootMounted";
import { useAuthStore } from "@/store/auth-store";
import { useNavigationStore } from "@/store/navigation-store";
import { NPTTEBrand } from "@/theme/branding";

export default function LoginScreen() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);
  const [pendingRole, setPendingRole] = useState<MobileRole | null>(null);
  const sessionExpired = useAuthStore((s) => s.sessionExpired);
  const rootMounted = useRootMounted();
  const replaceWhenReady = useNavigationStore((s) => s.replaceWhenReady);
  const navigatedRef = useRef(false);

  useEffect(() => {
    if (!pendingRole || !rootMounted || navigatedRef.current) return;
    navigatedRef.current = true;
    const href = mobileHomePath(pendingRole);
    replaceWhenReady(href);
    setPendingRole(null);
  }, [pendingRole, rootMounted, replaceWhenReady]);

  const onLogin = async () => {
    const trimmedUser = username.trim();
    if (!trimmedUser || !password) {
      setError("Enter username and password");
      return;
    }
    setLoading(true);
    setError(null);
    navigatedRef.current = false;
    try {
      await login({ username: trimmedUser, password });
      const [profile, perms] = await Promise.all([fetchProfile(), fetchPermissions()]);
      const role = resolveMobileRole(perms.role_code, perms.is_regulator);
      if (!role) {
        throw new Error(
          `No mobile role for account (${perms.role_code ?? "unknown"}). Contact your administrator.`
        );
      }
      useAuthStore.setState({
        profile,
        permissions: perms,
        mobileRole: role,
        loading: false,
        sessionExpired: false,
      });
      const bio = await isBiometricHardwareAvailable();
      const trust = await registerTrustedDevice(bio);
      if (!trust.success) {
        console.warn("Device trust registration skipped:", trust.message);
      }
      const pushChannel =
        role === "executive" ? "executive" : role === "regulator" ? "officer_tasks" : "officer_tasks";
      await initPushOrchestration(pushChannel);
      void sendDeviceHeartbeat();
      setPendingRole(role);
    } catch (e) {
      const msg = e instanceof Error ? e.message : "Login failed";
      if (msg.includes("abort") || msg.includes("network") || msg.includes("Failed to fetch")) {
        setError("Cannot reach NPTTE API. Check network or try again on Wi‑Fi/LTE.");
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
        <Text style={styles.hintTitle}>Demo accounts (Render demo seed)</Text>
        <Text style={styles.hintText}>nptte_admin / NptteAdmin2026!</Text>
        <Text style={styles.hintText}>demo_pharmacy_admin / DemoPharmacy2026!</Text>
        <Text style={styles.hintText}>demo_patient / DemoPatient2026!</Text>
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
