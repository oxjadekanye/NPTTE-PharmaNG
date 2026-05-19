import { useEffect, useRef } from "react";
import { Animated, StyleSheet, View } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

/** Readiness pulse under logo during sovereign boot. */
export function SplashReadinessPulse() {
  const scale = useRef(new Animated.Value(0.6)).current;
  const opacity = useRef(new Animated.Value(0.8)).current;

  useEffect(() => {
    const loop = Animated.loop(
      Animated.parallel([
        Animated.sequence([
          Animated.timing(scale, { toValue: 1.15, duration: 900, useNativeDriver: true }),
          Animated.timing(scale, { toValue: 0.6, duration: 900, useNativeDriver: true }),
        ]),
        Animated.sequence([
          Animated.timing(opacity, { toValue: 0.2, duration: 900, useNativeDriver: true }),
          Animated.timing(opacity, { toValue: 0.8, duration: 900, useNativeDriver: true }),
        ]),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [scale, opacity]);

  return (
    <View style={styles.wrap}>
      <Animated.View style={[styles.ring, { transform: [{ scale }], opacity }]} />
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: "center", marginTop: 24 },
  ring: {
    width: 56,
    height: 56,
    borderRadius: 28,
    borderWidth: 2,
    borderColor: NPTTEBrand.colors.sovereign.accent,
  },
});
