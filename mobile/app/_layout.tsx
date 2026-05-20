import { Stack, usePathname } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { BiometricGate } from "@/components/BiometricGate";
import { OperationalToast } from "@/components/OperationalToast";
import { useAuthStore } from "@/store/auth-store";
import { useEvidenceSync } from "@/hooks/useEvidenceSync";
import { useNetwork } from "@/hooks/useNetwork";
import { markAppReady, markAppStart, startTimer, endTimer } from "@/services/performance-monitor";
import { validateOfflineQueue } from "@/store/offline-queue";
import { NPTTEBrand } from "@/theme/branding";

SplashScreen.preventAutoHideAsync().catch(() => undefined);
markAppStart();

export default function RootLayout() {
  const hydrate = useAuthStore((s) => s.hydrate);
  const [deferOps, setDeferOps] = useState(false);
  const pathname = usePathname();

  useEffect(() => {
    startTimer(`route.${pathname}`);
    return () => endTimer("route", `route.${pathname}`);
  }, [pathname]);

  useEffect(() => {
    void hydrate().finally(() => {
      markAppReady();
      setDeferOps(true);
      void SplashScreen.hideAsync();
    });
  }, [hydrate]);

  return (
    <ErrorBoundary screenLabel="root">
      <StatusBar style="light" />
      <BiometricGate>
        <Stack
          screenOptions={{
            headerStyle: { backgroundColor: NPTTEBrand.colors.sovereign.bg },
            headerTintColor: NPTTEBrand.colors.sovereign.accent,
            contentStyle: { backgroundColor: NPTTEBrand.colors.sovereign.bg },
            headerShadowVisible: false,
            animation: "fade",
          }}
        >
          <Stack.Screen name="index" options={{ headerShown: false }} />
          <Stack.Screen name="login" options={{ title: "Staff login" }} />
          <Stack.Screen name="qa-dashboard" options={{ title: "Device QA" }} />
        </Stack>
      </BiometricGate>
      <OperationalToast />
      {deferOps ? <DeferredOps /> : null}
    </ErrorBoundary>
  );
}

function DeferredOps() {
  useNetwork();
  useEvidenceSync();
  useEffect(() => {
    validateOfflineQueue();
  }, []);
  return null;
}
