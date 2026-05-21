import { useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { usePathname } from "expo-router";
import { authenticateWithBiometrics, getBiometricEnabled } from "@/services/biometric";
import {
  isBiometricSessionGatePassed,
  markBiometricSessionGatePassed,
  resetBiometricSessionGate,
} from "@/services/biometric-session";
import { getAccessToken } from "@/services/auth-storage";
import { bootLog, BOOT_HARD_TIMEOUT_MS } from "@/services/boot-diagnostics";
import { useNavigationStore } from "@/store/navigation-store";

function isPublicRoute(pathname: string) {
  if (!pathname || pathname === "/" || pathname === "/login") return true;
  return pathname.startsWith("/citizen");
}

export function BiometricGate({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const [checking, setChecking] = useState(false);
  const [unlocked, setUnlocked] = useState(true);
  const [failed, setFailed] = useState(false);

  useEffect(() => {
    if (isPublicRoute(pathname)) {
      setUnlocked(true);
      setChecking(false);
      return;
    }

    if (isBiometricSessionGatePassed()) {
      setUnlocked(true);
      setChecking(false);
      return;
    }

    let cancelled = false;
    setChecking(true);
    bootLog("biometric", "session check start");

    const bypass = setTimeout(() => {
      if (cancelled) return;
      bootLog("biometric", "timeout — bypass gate");
      markBiometricSessionGatePassed();
      setUnlocked(true);
      setChecking(false);
    }, BOOT_HARD_TIMEOUT_MS);

    (async () => {
      try {
        const token = await getAccessToken();
        const enabled = await getBiometricEnabled();
        if (!token || !enabled) {
          if (!cancelled) {
            markBiometricSessionGatePassed();
            setUnlocked(true);
            setChecking(false);
            bootLog("biometric", "not required");
          }
          return;
        }
        const ok = await authenticateWithBiometrics();
        if (cancelled) return;
        if (ok) markBiometricSessionGatePassed();
        setUnlocked(ok);
        setFailed(!ok);
        setChecking(false);
        bootLog("biometric", ok ? "session unlocked" : "failed");
      } catch (err) {
        if (!cancelled) {
          markBiometricSessionGatePassed();
          setUnlocked(true);
          setChecking(false);
          bootLog("biometric", `error bypass ${err instanceof Error ? err.message : ""}`);
        }
      } finally {
        clearTimeout(bypass);
      }
    })();

    return () => {
      cancelled = true;
      clearTimeout(bypass);
    };
  }, [pathname]);

  if (isPublicRoute(pathname)) return <>{children}</>;

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
          if (ok) {
            markBiometricSessionGatePassed();
            setUnlocked(true);
          } else {
            setFailed(true);
          }
        }}
      >
        <Text style={styles.btnText}>Unlock with biometrics</Text>
      </Pressable>
      <Pressable
        onPress={() => {
          resetBiometricSessionGate();
          useNavigationStore.getState().replaceWhenReady("/login");
        }}
      >
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
