import { useEffect, useRef } from "react";
import { Animated, Easing, Pressable, StyleSheet, Text, View } from "react-native";
import { router } from "expo-router";
import { CITIZEN_ROUTES, pushCitizenRoute } from "@/services/citizen-navigation";
import { landingLog, openStaffLogin } from "@/navigation/staff-login-intent";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";
import {
  ctaShadow,
  LANDING_CTA_MIN_HEIGHT,
  LANDING_CTA_VARIANTS,
  landingShared,
  type LandingCtaVariant,
} from "@/components/landing/landing-styles";

type Props = {
  href: string;
  label: string;
  variant: LandingCtaVariant;
  delay: number;
  slide: Animated.Value;
  publicFlow?: boolean;
  accessibilityLabel?: string;
};

export function LandingCtaButton({
  href,
  label,
  variant,
  delay,
  slide,
  publicFlow,
  accessibilityLabel,
}: Props) {
  const setBypassAutoRedirect = useLandingIntent((s) => s.setBypassAutoRedirect);
  const entryOpacity = useRef(new Animated.Value(0)).current;
  const pressScale = useRef(new Animated.Value(1)).current;
  const glowPulse = useRef(new Animated.Value(0.55)).current;
  const tokens = LANDING_CTA_VARIANTS[variant];

  useEffect(() => {
    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.timing(entryOpacity, { toValue: 1, duration: 400, useNativeDriver: true }),
        Animated.timing(slide, { toValue: 0, duration: 440, easing: Easing.out(Easing.cubic), useNativeDriver: true }),
      ]),
    ]).start();
  }, [delay, entryOpacity, slide]);

  useEffect(() => {
    const loop = Animated.loop(
      Animated.sequence([
        Animated.timing(glowPulse, { toValue: 1, duration: 2000, useNativeDriver: true }),
        Animated.timing(glowPulse, { toValue: 0.55, duration: 2000, useNativeDriver: true }),
      ])
    );
    loop.start();
    return () => loop.stop();
  }, [glowPulse]);

  const onPress = () => {
    if (href === "/login") {
      landingLog("staff_login_pressed");
      openStaffLogin();
      return;
    }
    if (publicFlow) setBypassAutoRedirect(true);
    if (href.startsWith("/citizen")) {
      pushCitizenRoute(href as (typeof CITIZEN_ROUTES)[keyof typeof CITIZEN_ROUTES]);
      return;
    }
    useNavigationStore.getState().pushWhenReady(href);
  };

  return (
    <Animated.View
      style={[
        styles.wrap,
        { opacity: entryOpacity, transform: [{ translateY: slide }, { scale: pressScale }] },
      ]}
      pointerEvents="box-none"
    >
      <Animated.View
        pointerEvents="none"
        style={[
          landingShared.ctaGlowRing,
          styles.glowRing,
          { borderColor: tokens.border, opacity: glowPulse },
        ]}
      />
      <Pressable
        style={({ pressed }) => [
          styles.btn,
          { backgroundColor: tokens.fill, borderColor: tokens.border },
          ctaShadow(tokens.glow),
          pressed && styles.btnPressed,
        ]}
        pointerEvents="auto"
        accessibilityRole="button"
        accessibilityLabel={accessibilityLabel ?? label}
        onPressIn={() => {
          Animated.spring(pressScale, { toValue: 0.96, useNativeDriver: true, speed: 50, bounciness: 0 }).start();
        }}
        onPressOut={() => {
          Animated.spring(pressScale, { toValue: 1, useNativeDriver: true, speed: 40, bounciness: 5 }).start();
        }}
        onPress={onPress}
      >
        <View
          pointerEvents="none"
          style={[landingShared.ctaHighlight, { backgroundColor: tokens.fillHighlight }]}
        />
        <View style={landingShared.ctaRow} pointerEvents="none">
          <View style={landingShared.ctaIconWrap}>
            <Text style={landingShared.ctaIcon}>{tokens.icon}</Text>
          </View>
          <Text style={landingShared.ctaLabel}>{label}</Text>
        </View>
      </Pressable>
    </Animated.View>
  );
}

const styles = StyleSheet.create({
  wrap: {
    position: "relative",
    zIndex: 12,
    marginBottom: 2,
  },
  glowRing: {
    zIndex: 0,
  },
  btn: {
    minHeight: LANDING_CTA_MIN_HEIGHT,
    borderRadius: 14,
    borderWidth: 2,
    justifyContent: "center",
    overflow: "hidden",
    zIndex: 1,
  },
  btnPressed: {
    opacity: 0.92,
  },
});
