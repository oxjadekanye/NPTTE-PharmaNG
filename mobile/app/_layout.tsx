import { Stack } from "expo-router";
import { StatusBar } from "expo-status-bar";
import { useEffect } from "react";
import { BiometricGate } from "@/components/BiometricGate";
import { useAuthStore } from "@/store/auth-store";
import { useEvidenceSync } from "@/hooks/useEvidenceSync";

export default function RootLayout() {
  const hydrate = useAuthStore((s) => s.hydrate);
  useEvidenceSync();

  useEffect(() => {
    void hydrate();
  }, [hydrate]);

  return (
    <>
      <StatusBar style="light" />
      <BiometricGate>
        <Stack
          screenOptions={{
            headerStyle: { backgroundColor: "#020617" },
            headerTintColor: "#38bdf8",
            contentStyle: { backgroundColor: "#020617" },
          }}
        />
      </BiometricGate>
    </>
  );
}
