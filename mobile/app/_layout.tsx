import { Stack } from "expo-router";
import * as SplashScreen from "expo-splash-screen";
import { StatusBar } from "expo-status-bar";
import { useEffect, useState } from "react";
import { BiometricGate } from "@/components/BiometricGate";
import { useAuthStore } from "@/store/auth-store";
import { useEvidenceSync } from "@/hooks/useEvidenceSync";
import { NPTTEBrand } from "@/theme/branding";

SplashScreen.preventAutoHideAsync().catch(() => undefined);

export default function RootLayout() {
  const hydrate = useAuthStore((s) => s.hydrate);
  const [deferOps, setDeferOps] = useState(false);
  useEffect(() => {
    void hydrate()
      .finally(() => {
        setDeferOps(true);
        void SplashScreen.hideAsync();
      });
  }, [hydrate]);

  return (
    <>
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
        </Stack>
      </BiometricGate>
      {deferOps ? <DeferredOps /> : null}
    </>
  );
}

function DeferredOps() {
  useEvidenceSync();
  return null;
}
