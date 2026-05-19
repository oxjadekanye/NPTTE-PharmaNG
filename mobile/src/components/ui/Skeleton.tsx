import { useEffect, useRef } from "react";
import { Animated, StyleSheet, View, type ViewStyle } from "react-native";
import { NPTTEBrand } from "@/theme/branding";

export function Skeleton({
  width = "100%",
  height = 16,
  style,
}: {
  width?: number | `${number}%`;
  height?: number;
  style?: ViewStyle;
}) {
  const pulse = useRef(new Animated.Value(0.35)).current;

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(pulse, { toValue: 0.7, duration: 700, useNativeDriver: true }),
        Animated.timing(pulse, { toValue: 0.35, duration: 700, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [pulse]);

  return (
    <Animated.View
      style={[
        styles.base,
        { width, height, opacity: pulse },
        style,
      ]}
    />
  );
}

export function SkeletonCard() {
  return (
    <View style={styles.card}>
      <Skeleton height={14} width="40%" />
      <Skeleton height={22} width="70%" style={{ marginTop: 10 }} />
      <Skeleton height={12} width="90%" style={{ marginTop: 12 }} />
    </View>
  );
}

const styles = StyleSheet.create({
  base: {
    backgroundColor: NPTTEBrand.colors.sovereign.elevated,
    borderRadius: NPTTEBrand.radius.sm,
  },
  card: {
    backgroundColor: NPTTEBrand.colors.sovereign.surface,
    borderRadius: NPTTEBrand.radius.md,
    padding: NPTTEBrand.spacing.lg,
    marginBottom: NPTTEBrand.spacing.md,
    borderWidth: 1,
    borderColor: NPTTEBrand.colors.sovereign.border,
  },
});
