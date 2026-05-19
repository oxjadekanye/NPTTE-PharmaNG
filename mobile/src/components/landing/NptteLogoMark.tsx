import { useEffect, useRef } from "react";
import { Animated, Easing, Image, StyleSheet, type ImageStyle } from "react-native";
import { splashLogo } from "@/assets/branding-images";

type Props = {
  /** Logo width in dp — height scales with aspect ratio */
  width?: number;
  style?: ImageStyle;
};

export function NptteLogoMark({ width = 260, style }: Props) {
  const pulse = useRef(new Animated.Value(0)).current;
  const glow = useRef(new Animated.Value(0.92)).current;

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.parallel([
          Animated.timing(pulse, {
            toValue: 1,
            duration: 2400,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
          Animated.timing(glow, {
            toValue: 1,
            duration: 2400,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
        ]),
        Animated.parallel([
          Animated.timing(pulse, {
            toValue: 0,
            duration: 2400,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
          Animated.timing(glow, {
            toValue: 0.92,
            duration: 2400,
            easing: Easing.inOut(Easing.sin),
            useNativeDriver: true,
          }),
        ]),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [pulse, glow]);

  const scale = pulse.interpolate({ inputRange: [0, 1], outputRange: [1, 1.03] });
  const height = width * 0.92;

  return (
    <Animated.View style={[styles.wrap, { transform: [{ scale }], opacity: glow }]}>
      <Image
        source={splashLogo}
        style={[styles.logo, { width, height }, style]}
        resizeMode="contain"
        accessibilityLabel="NPTTE PharmaNG"
      />
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: "center" },
  logo: {},
});
