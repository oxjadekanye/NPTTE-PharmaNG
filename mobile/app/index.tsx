import { router } from "expo-router";
import { useEffect, useState } from "react";
import { View, StyleSheet } from "react-native";
import { useSafeNavigation } from "@/hooks/useSafeNavigation";
import { mobileHomePath } from "@/services/role-routing";
import { ProductionLandingScreen } from "@/components/landing/ProductionLandingScreen";
import { LandingBootSplash } from "@/components/landing/LandingBootSplash";
import { useAuthStore } from "@/store/auth-store";

export default function LandingRoute() {
  const { loading, mobileRole, hydrate } = useAuthStore();
  const { safeReplace } = useSafeNavigation();
  const [bootDone, setBootDone] = useState(false);

  useEffect(() => {
    void hydrate().then((role) => {
      if (role) safeReplace(mobileHomePath(role));
      setBootDone(true);
    });
  }, [hydrate, safeReplace]);

  if (mobileRole) return null;

  const showBoot = loading || !bootDone;

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
