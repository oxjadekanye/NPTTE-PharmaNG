import { Stack } from "expo-router";
import { NPTTEBrand } from "@/theme/branding";

const screenOptions = {
  headerStyle: { backgroundColor: NPTTEBrand.colors.sovereign.bg },
  headerTintColor: NPTTEBrand.colors.sovereign.accent,
  contentStyle: { backgroundColor: NPTTEBrand.colors.sovereign.bg },
  headerShadowVisible: false,
};

export default function CitizenLayout() {
  return (
    <Stack screenOptions={screenOptions}>
      <Stack.Screen name="index" options={{ title: "Citizen verification" }} />
      <Stack.Screen name="scan" options={{ title: "Scan or verify" }} />
      <Stack.Screen name="manual" options={{ title: "Manual lookup" }} />
      <Stack.Screen name="recalls" options={{ title: "Recall alerts" }} />
      <Stack.Screen name="report" options={{ title: "Report counterfeit" }} />
    </Stack>
  );
}
