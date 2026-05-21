import { Stack, usePathname } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useEffect, useRef } from "react";
import { SafeAreaProvider } from "react-native-safe-area-context";
import { AuthNavigationBridge } from "@/components/AuthNavigationBridge";
import { ErrorBoundary } from "@/components/ErrorBoundary";
import { BiometricGate } from "@/components/BiometricGate";
import { OperationalToast } from "@/components/OperationalToast";
import { useAuthStore } from "@/store/auth-store";
import { useEvidenceSync } from "@/hooks/useEvidenceSync";
import { useNetwork } from "@/hooks/useNetwork";
import { bootLog, BOOT_HARD_TIMEOUT_MS } from "@/services/boot-diagnostics";
import { markAppReady, markAppStart } from "@/services/performance-monitor";
import { useNavigationStore } from "@/store/navigation-store";
import { validateOfflineQueue } from "@/store/offline-queue";
import { NPTTEBrand } from "@/theme/branding";

SplashScreen.preventAutoHideAsync().catch(() => undefined);
markAppStart();

export default function RootLayout() {
  const pathname = usePathname();
  const bootStarted = useRef(false);
  const setRootMounted = useNavigationStore((s) => s.setRootMounted);

  useEffect(() => {
    const id = requestAnimationFrame(() => {
      setRootMounted();
    });
    return () => cancelAnimationFrame(id);
  }, [setRootMounted]);

  useEffect(() => {
    if (bootStarted.current) return;
    bootStarted.current = true;
    bootLog("root layout", "hydrate start");

    const forceSplashHide = setTimeout(() => {
      bootLog("splash", "force hide (timeout)");
      markAppReady();
      void SplashScreen.hideAsync().catch(() => undefined);
    }, BOOT_HARD_TIMEOUT_MS);

    const hydrate = useAuthStore.getState().hydrate;
    void hydrate()
      .catch((err) => {
        bootLog("auth hydrate", `failed ${err instanceof Error ? err.message : "unknown"}`);
      })
      .finally(() => {
        clearTimeout(forceSplashHide);
        bootLog("splash", "hide after hydrate");
        markAppReady();
        void SplashScreen.hideAsync().catch(() => undefined);
      });

    return () => clearTimeout(forceSplashHide);
  }, []);

  useEffect(() => {
    bootLog("route", pathname || "/");
  }, [pathname]);

  return (
    <SafeAreaProvider>
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
        <AuthNavigationBridge />
        <DeferredOps />
      </ErrorBoundary>
    </SafeAreaProvider>
  );
}

/** Non-blocking background ops — never gate first paint. */
function DeferredOps() {
  useNetwork();
  useEvidenceSync();
  useEffect(() => {
    bootLog("deferred ops", "offline queue validate");
    try {
      validateOfflineQueue();
    } catch (err) {
      bootLog("deferred ops", `queue validate failed ${err instanceof Error ? err.message : ""}`);
    }
  }, []);
  return null;
}
