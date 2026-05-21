import { Link, router, type Href } from "expo-router";
import { useEffect, useRef } from "react";
import { useQaMode } from "@/store/qa-mode-store";
import { useLandingIntent } from "@/store/landing-intent-store";
import {
  Animated,
  Dimensions,
  Easing,
  Platform,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from "react-native";
import { useSafeAreaInsets } from "react-native-safe-area-context";
import { NptteLogoMark } from "@/components/landing/NptteLogoMark";
import { OperationalFooter } from "@/components/landing/OperationalFooter";

const { height: SCREEN_H } = Dimensions.get("window");
const isCompact = SCREEN_H < 740;

type ActionProps = {
  href: Href;
  label: string;
  variant: "primary" | "secondary" | "accent" | "alert";
  delay: number;
  slide: Animated.Value;
  publicFlow?: boolean;
};

function LandingAction({ href, label, variant, delay, slide, publicFlow }: ActionProps) {
  const setBypassAutoRedirect = useLandingIntent((s) => s.setBypassAutoRedirect);
  const opacity = useRef(new Animated.Value(0)).current;

  useEffect(() => {
    Animated.sequence([
      Animated.delay(delay),
      Animated.parallel([
        Animated.timing(opacity, { toValue: 1, duration: 380, useNativeDriver: true }),
        Animated.timing(slide, { toValue: 0, duration: 420, easing: Easing.out(Easing.cubic), useNativeDriver: true }),
      ]),
    ]).start();
  }, [delay, opacity, slide]);

  const variantStyle =
    variant === "primary"
      ? styles.btnPrimary
      : variant === "accent"
        ? styles.btnAccent
        : variant === "alert"
          ? styles.btnAlert
          : styles.btnSecondary;

  const textStyle =
    variant === "secondary" ? styles.btnTextSecondary : styles.btnTextPrimary;

  return (
    <Animated.View style={{ opacity, transform: [{ translateY: slide }] }}>
      <Link href={href} asChild>
        <Pressable
          style={({ pressed }) => [variantStyle, pressed && styles.btnPressed]}
          onPress={() => {
            if (publicFlow) setBypassAutoRedirect(true);
          }}
        >
          <Text style={textStyle}>{label}</Text>
        </Pressable>
      </Link>
    </Animated.View>
  );
}

export function ProductionLandingScreen() {
  const unlockQa = useQaMode((s) => s.unlock);
  const insets = useSafeAreaInsets();
  const headerFade = useRef(new Animated.Value(0)).current;
  const headerSlide = useRef(new Animated.Value(24)).current;
  const actionsSlide = useRef(new Animated.Value(28)).current;

  useEffect(() => {
    Animated.parallel([
      Animated.timing(headerFade, { toValue: 1, duration: 520, useNativeDriver: true }),
      Animated.timing(headerSlide, {
        toValue: 0,
        duration: 560,
        easing: Easing.out(Easing.cubic),
        useNativeDriver: true,
      }),
    ]).start();
  }, [headerFade, headerSlide]);

  const bottomPad = Math.max(insets.bottom, Platform.OS === "android" ? 20 : 12);

  return (
    <View style={[styles.root, { paddingTop: insets.top + (isCompact ? 8 : 16) }]}>
      <View style={styles.gridBg} pointerEvents="none">
        <View style={styles.gridLineH} />
        <View style={styles.gridLineV} />
        <View style={styles.glowOrb} />
      </View>
      <ScrollView
        contentContainerStyle={[
          styles.scroll,
          { paddingBottom: bottomPad + 12, paddingHorizontal: isCompact ? 20 : 24 },
        ]}
        showsVerticalScrollIndicator={false}
        bounces={false}
      >
        <Animated.View
          style={{
            opacity: headerFade,
            transform: [{ translateY: headerSlide }],
            alignItems: "center",
          }}
        >
          <Pressable
            onLongPress={() => {
              unlockQa();
              router.push("/qa-dashboard" as Href);
            }}
            delayLongPress={2800}
          >
            <NptteLogoMark width={isCompact ? 220 : 260} />
          </Pressable>
          <Text style={styles.subtitle}>
            National Pharmaceutical Traceability &{"\n"}Enforcement Platform
          </Text>
          <View style={styles.badge}>
            <View style={styles.badgeDot} />
            <Text style={styles.badgeText}>LIVE • Sovereign Infrastructure</Text>
          </View>
        </Animated.View>

        <View style={[styles.actions, isCompact && styles.actionsCompact]}>
          <LandingAction
            href="/citizen"
            label="Citizen Verification"
            variant="primary"
            delay={180}
            slide={actionsSlide}
            publicFlow
          />
          <LandingAction
            href="/login"
            label="Staff Login"
            variant="secondary"
            delay={260}
            slide={actionsSlide}
          />
          <LandingAction
            href="/citizen/recalls"
            label="Emergency Recall Alerts"
            variant="accent"
            delay={340}
            slide={actionsSlide}
            publicFlow
          />
          <LandingAction
            href="/citizen/report"
            label="Report Suspicious Medicine"
            variant="alert"
            delay={420}
            slide={actionsSlide}
            publicFlow
          />
        </View>

        <OperationalFooter />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: { flex: 1, backgroundColor: "#020617" },
  gridBg: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "#020617",
  },
  gridLineH: {
    position: "absolute",
    top: "22%",
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: "#1e293b44",
  },
  gridLineV: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: "50%",
    width: 1,
    backgroundColor: "#1e293b33",
  },
  glowOrb: {
    position: "absolute",
    top: -80,
    alignSelf: "center",
    width: 280,
    height: 280,
    borderRadius: 140,
    backgroundColor: "#0284c722",
  },
  scroll: { flexGrow: 1, justifyContent: "space-between" },
  subtitle: {
    fontSize: 14,
    color: "#94a3b8",
    textAlign: "center",
    marginTop: 12,
    lineHeight: 22,
    maxWidth: 340,
    paddingHorizontal: 8,
  },
  badge: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: 18,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 999,
    backgroundColor: "#14532d55",
    borderWidth: 1,
    borderColor: "#22c55e66",
  },
  badgeDot: {
    width: 8,
    height: 8,
    borderRadius: 4,
    backgroundColor: "#4ade80",
    marginRight: 8,
  },
  badgeText: {
    color: "#86efac",
    fontSize: 11,
    fontWeight: "700",
    letterSpacing: 0.6,
  },
  actions: { marginTop: 36, gap: 12 },
  actionsCompact: { marginTop: 24, gap: 10 },
  btnPrimary: {
    backgroundColor: "#0284c7",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    shadowColor: "#0284c7",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.35,
    shadowRadius: 12,
    elevation: 8,
  },
  btnSecondary: {
    backgroundColor: "#0f172a",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#334155",
    shadowColor: "#000",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 8,
    elevation: 4,
  },
  btnAccent: {
    backgroundColor: "#1e3a5f",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#38bdf866",
    shadowColor: "#38bdf8",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 10,
    elevation: 5,
  },
  btnAlert: {
    backgroundColor: "#7f1d1d",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#f8717166",
    shadowColor: "#ef4444",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.25,
    shadowRadius: 10,
    elevation: 5,
  },
  btnPressed: { opacity: 0.88, transform: [{ scale: 0.99 }] },
  btnTextPrimary: { color: "#ffffff", fontWeight: "700", fontSize: 16, letterSpacing: 0.2 },
  btnTextSecondary: { color: "#38bdf8", fontWeight: "700", fontSize: 16, letterSpacing: 0.2 },
});
