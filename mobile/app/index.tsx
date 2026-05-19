import { router } from "expo-router";
import { useEffect, useState } from "react";
import { View, StyleSheet } from "react-native";
import { mobileHomePath } from "@/services/role-routing";
import { ProductionLandingScreen } from "@/components/landing/ProductionLandingScreen";
import { LandingBootSplash } from "@/components/landing/LandingBootSplash";
import { useAuthStore } from "@/store/auth-store";

export default function LandingRoute() {
  const { loading, mobileRole, hydrate } = useAuthStore();
  const [bootDone, setBootDone] = useState(false);

  useEffect(() => {
    void hydrate().then((role) => {
      if (role) router.replace(mobileHomePath(role));
      setBootDone(true);
    });
  }, [hydrate]);

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
  root: { flex: 1, backgroundColor: "#020617" },
});
