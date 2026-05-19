import { useEffect, useRef, useState } from "react";
import { Animated, StyleSheet, Text, View } from "react-native";
import { NptteLogoMark } from "@/components/landing/NptteLogoMark";
import { SplashReadinessPulse } from "@/components/landing/SplashReadinessPulse";
import { NPTTEBrand } from "@/theme/branding";

/** Branded boot overlay — fades out into the production landing screen. */
export function LandingBootSplash({ visible }: { visible: boolean }) {
  const opacity = useRef(new Animated.Value(1)).current;
  const [mounted, setMounted] = useState(true);

  useEffect(() => {
    if (visible) {
      setMounted(true);
      opacity.setValue(1);
      return;
    }
    Animated.timing(opacity, { toValue: 0, duration: 320, useNativeDriver: true }).start(({ finished }) => {
      if (finished) setMounted(false);
    });
  }, [visible, opacity]);

  if (!mounted) return null;

  return (
    <Animated.View style={[styles.overlay, { opacity }]} pointerEvents={visible ? "auto" : "none"}>
      <NptteLogoMark />
      <Text style={styles.title}>{NPTTEBrand.name}</Text>
      <SplashReadinessPulse />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: NPTTEBrand.colors.sovereign.bg,
    alignItems: "center",
    justifyContent: "center",
    zIndex: 100,
  },
  title: { color: "#f8fafc", fontSize: 22, fontWeight: "700", marginTop: 20 },
});
