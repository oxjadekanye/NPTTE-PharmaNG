import { useEffect, useRef } from "react";
import { Animated, Easing, StyleSheet, Text, View } from "react-native";

export function NptteLogoMark() {
  const pulse = useRef(new Animated.Value(0)).current;
  const glow = useRef(new Animated.Value(0.4)).current;

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.parallel([
          Animated.timing(pulse, {
            toValue: 1,
            duration: 2200,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
          Animated.timing(glow, {
            toValue: 1,
            duration: 2200,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
        ]),
        Animated.parallel([
          Animated.timing(pulse, {
            toValue: 0,
            duration: 2200,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
          Animated.timing(glow, {
            toValue: 0.4,
            duration: 2200,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
        ]),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [pulse, glow]);

  const scale = pulse.interpolate({ inputRange: [0, 1], outputRange: [1, 1.04] });

  return (
    <Animated.View style={[styles.wrap, { transform: [{ scale }], opacity: glow }]}>
      <View style={styles.ring}>
        <View style={styles.core}>
          <Text style={styles.glyph}>N</Text>
        </View>
      </View>
      <View style={styles.accent} />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: "center", marginBottom: 4 },
  ring: {
    width: 88,
    height: 88,
    borderRadius: 44,
    borderWidth: 2,
    borderColor: "#38bdf8",
    alignItems: "center",
    justifyContent: "center",
    backgroundColor: "#0f172a",
    shadowColor: "#38bdf8",
    shadowOffset: { width: 0, height: 0 },
    shadowOpacity: 0.45,
    shadowRadius: 16,
    elevation: 12,
  },
  core: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: "#0284c7",
    alignItems: "center",
    justifyContent: "center",
  },
  glyph: { color: "#f8fafc", fontSize: 32, fontWeight: "800", letterSpacing: -1 },
  accent: {
    position: "absolute",
    bottom: -4,
    width: 48,
    height: 3,
    borderRadius: 2,
    backgroundColor: "#22c55e",
  },
});
