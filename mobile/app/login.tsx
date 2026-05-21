import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, Text, TextInput, View } from "react-native";
import { PasswordInput } from "@/components/PasswordInput";
import { LoginSection } from "@/components/login/LoginSection";
import { loginFieldStyles as styles } from "@/components/login/login-styles";
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
  { user: "nptte_admin", password: "NptteAdmin2026!", role: "Regulator / executive" },
  { user: "demo_pharmacy_admin", password: "DemoPharmacy2026!", role: "Pharmacy" },
  { user: "demo_patient", password: "DemoPatient2026!", role: "Citizen" },
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
      {sessionExpired && (
        <LoginSection
          variant="warning"
          title="Session expired"
          subtitle="Your previous session ended. Sign in again to continue."
        >
          <Text style={[styles.message, { color: NPTTEBrand.colors.alert.warning }]}>
            For your security, field officer sessions require re-authentication after timeout.
          </Text>
        </LoginSection>
      )}

      <LoginSection
        variant="credentials"
        title="1. Enter credentials"
        subtitle="Staff username and password (case sensitive)"
      >
        <View>
          <Text style={styles.label}>Username</Text>
          <TextInput
            style={styles.input}
            placeholder="e.g. nptte_admin"
            placeholderTextColor={NPTTEBrand.colors.sovereign.muted}
            autoCapitalize="none"
            autoCorrect={false}
            value={username}
            onChangeText={setUsername}
            editable={!loading}
            accessibilityLabel="Username"
          />
        </View>
        <View>
          <Text style={styles.label}>Password</Text>
          <PasswordInput
            placeholder="Enter password"
            value={password}
            onChangeText={setPassword}
            editable={!loading}
            onSubmitEditing={() => void onLogin()}
            style={styles.input}
            containerStyle={{ marginBottom: 0 }}
          />
        </View>
      </LoginSection>

      {error ? (
        <LoginSection variant="error" title="Sign-in issue" subtitle="Correct the details below and try again">
          <Text style={[styles.message, { color: "#fca5a5" }]}>{error}</Text>
        </LoginSection>
      ) : null}

      <LoginSection variant="action" title="2. Sign in" subtitle="Opens your role home after successful authentication">
        <Pressable
          style={styles.btn}
          onPress={() => void onLogin()}
          disabled={loading}
          accessibilityRole="button"
          accessibilityLabel="Sign in"
        >
          {loading ? (
            <ActivityIndicator color="#fff" />
          ) : (
            <Text style={styles.btnText}>Sign in to NPTTE</Text>
          )}
        </Pressable>
      </LoginSection>

      <LoginSection
        variant="info"
        title="3. Demo accounts"
        subtitle="Exact credentials — copy carefully (case sensitive)"
      >
        {DEMO_ACCOUNTS.map((row) => (
          <View key={row.user} style={styles.demoRow}>
            <Text style={styles.hintUser}>{row.role}</Text>
            <Text style={styles.hintUser}>Username: {row.user}</Text>
            <Text style={styles.hintPass}>Password: {row.password}</Text>
          </View>
        ))}
        <Text style={styles.hintSub}>Seed on Render: python manage.py seed_demo_data</Text>
      </LoginSection>
    </ScreenShell>
  );
}
