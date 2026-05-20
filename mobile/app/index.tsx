import { router } from "expo-router";
import { useEffect, useRef, useState } from "react";
import { View, StyleSheet } from "react-native";
import { ProductionLandingScreen } from "@/components/landing/ProductionLandingScreen";
import { LandingBootSplash } from "@/components/landing/LandingBootSplash";
import { bootLog, BOOT_HARD_TIMEOUT_MS } from "@/services/boot-diagnostics";
import { mobileHomePath } from "@/services/role-routing";
import { useAuthStore } from "@/store/auth-store";

export default function LandingRoute() {
  const loading = useAuthStore((s) => s.loading);
  const mobileRole = useAuthStore((s) => s.mobileRole);
  const [bootDone, setBootDone] = useState(false);
  const navigatedRef = useRef(false);

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
    if (!mobileRole || navigatedRef.current) return;
    navigatedRef.current = true;
    const href = mobileHomePath(mobileRole);
    bootLog("navigation", `redirect to ${href}`);
    setBootDone(true);
    router.replace(href as never);
  }, [mobileRole]);

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
