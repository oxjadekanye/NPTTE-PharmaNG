import { useEffect, useRef, useState } from "react";
import { View, StyleSheet } from "react-native";
import { ProductionLandingScreen } from "@/components/landing/ProductionLandingScreen";
import { LandingBootSplash } from "@/components/landing/LandingBootSplash";
import { useRootMounted } from "@/hooks/useRootMounted";
import { bootLog, BOOT_HARD_TIMEOUT_MS } from "@/services/boot-diagnostics";
import { mobileHomePath } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";

export default function LandingRoute() {
  const loading = useAuthStore((s) => s.loading);
  const mobileRole = useAuthStore((s) => s.mobileRole);
  const [bootDone, setBootDone] = useState(false);
  const navigatedRef = useRef(false);
  const bypassAutoRedirect = useLandingIntent((s) => s.bypassAutoRedirect);
  const setBypassAutoRedirect = useLandingIntent((s) => s.setBypassAutoRedirect);
  const rootMounted = useRootMounted();
  const replaceWhenReady = useNavigationStore((s) => s.replaceWhenReady);

  useEffect(() => {
    bootLog("landing", "mount");
    const forceLanding = setTimeout(() => {
      bootLog("landing", "timeout — reveal landing");
      setBootDone(true);
    }, BOOT_HARD_TIMEOUT_MS);

    return () => clearTimeout(forceLanding);
  }, []);

  useEffect(() => {
    if (loading) return;
    bootLog("landing", "auth loading complete");
    setBootDone(true);
  }, [loading]);

  useEffect(() => {
    if (!rootMounted || !mobileRole || navigatedRef.current || bypassAutoRedirect) return;
    navigatedRef.current = true;
    const href = mobileHomePath(mobileRole);
    bootLog("navigation", `landing redirect queued → ${href}`);
    setBootDone(true);
    replaceWhenReady(href);
  }, [mobileRole, bypassAutoRedirect, rootMounted, replaceWhenReady]);

  useEffect(() => {
    return () => setBypassAutoRedirect(false);
  }, [setBypassAutoRedirect]);

  const showBoot = !bootDone;

  return (
    <View style={styles.root}>
      <ProductionLandingScreen />
      <LandingBootSplash visible={showBoot} />
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#000000" },
});
