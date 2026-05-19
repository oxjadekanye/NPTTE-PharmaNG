import { useEffect, useRef, useState } from "react";
import { Animated, StyleSheet } from "react-native";
import { NptteLogoMark } from "@/components/landing/NptteLogoMark";
import { SplashReadinessPulse } from "@/components/landing/SplashReadinessPulse";

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
      <NptteLogoMark width={280} />
      <SplashReadinessPulse />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  overlay: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "#000000",
    alignItems: "center",
    justifyContent: "center",
    zIndex: 100,
  },
});
