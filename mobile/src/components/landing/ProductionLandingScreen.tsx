import { router } from "expo-router";
import { useEffect, useRef } from "react";
import { useQaMode } from "@/store/qa-mode-store";
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
import { LandingCtaButton } from "@/components/landing/LandingCtaButton";
import { LANDING_COLORS } from "@/components/landing/landing-styles";

const { height: SCREEN_H } = Dimensions.get("window");
const isCompact = SCREEN_H < 740;

export function ProductionLandingScreen() {
  const unlockQa = useQaMode((s) => s.unlock);
  const insets = useSafeAreaInsets();
  const headerFade = useRef(new Animated.Value(0)).current;
  const headerSlide = useRef(new Animated.Value(24)).current;
  const actionsSlide = useRef(new Animated.Value(32)).current;

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

  const bottomPad = Math.max(insets.bottom, Platform.OS === "android" ? 24 : 16);

  return (
    <View style={[styles.root, { paddingTop: insets.top + (isCompact ? 10 : 18) }]}>
      <View style={styles.gridBg} pointerEvents="none">
        <View style={styles.bgGradientTop} pointerEvents="none" />
        <View style={styles.bgGradientBottom} pointerEvents="none" />
        <View style={styles.gridLineH} pointerEvents="none" />
        <View style={styles.gridLineH2} pointerEvents="none" />
        <View style={styles.gridLineV} pointerEvents="none" />
        <View style={styles.glowOrbCyan} pointerEvents="none" />
        <View style={styles.glowOrbViolet} pointerEvents="none" />
      </View>

      <ScrollView
        contentContainerStyle={[
          styles.scroll,
          { paddingBottom: bottomPad + 16, paddingHorizontal: isCompact ? 18 : 22 },
        ]}
        showsVerticalScrollIndicator={false}
        bounces={false}
        keyboardShouldPersistTaps="handled"
      >
        <Animated.View
          style={[styles.header, { opacity: headerFade, transform: [{ translateY: headerSlide }] }]}
          pointerEvents="box-none"
        >
          <Pressable
            onLongPress={() => {
              unlockQa();
              router.push("/qa-dashboard" as never);
            }}
            delayLongPress={2800}
            accessibilityRole="imagebutton"
            accessibilityLabel="NPTTE logo"
          >
            <NptteLogoMark width={isCompact ? 228 : 268} />
          </Pressable>
          <Text style={styles.subtitle}>
            National Pharmaceutical Traceability &{"\n"}Enforcement Platform
          </Text>
          <View style={styles.badge} pointerEvents="none">
            <View style={styles.badgeDot} />
            <Text style={styles.badgeText}>LIVE • Sovereign Infrastructure</Text>
          </View>
        </Animated.View>

        <View style={[styles.actions, isCompact && styles.actionsCompact]} pointerEvents="box-none">
          <LandingCtaButton
            href="/citizen"
            label="Citizen Verification"
            variant="primary"
            delay={180}
            slide={actionsSlide}
            publicFlow
            accessibilityLabel="Open citizen verification"
          />
          <LandingCtaButton
            href="/login"
            label="Staff Login"
            variant="staff"
            delay={260}
            slide={actionsSlide}
            accessibilityLabel="Open staff login"
          />
          <LandingCtaButton
            href="/citizen/recalls"
            label="Emergency Recall Alerts"
            variant="accent"
            delay={340}
            slide={actionsSlide}
            publicFlow
            accessibilityLabel="View emergency recall alerts"
          />
          <LandingCtaButton
            href="/citizen/report"
            label="Report Suspicious Medicine"
            variant="alert"
            delay={420}
            slide={actionsSlide}
            publicFlow
            accessibilityLabel="Report suspicious medicine"
          />
        </View>

        <OperationalFooter />
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  root: {
    flex: 1,
    backgroundColor: LANDING_COLORS.bg,
  },
  gridBg: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: LANDING_COLORS.bg,
    zIndex: 0,
  },
  bgGradientTop: {
    position: "absolute",
    top: 0,
    left: 0,
    right: 0,
    height: "45%",
    backgroundColor: LANDING_COLORS.bgMid,
    opacity: 0.85,
  },
  bgGradientBottom: {
    position: "absolute",
    bottom: 0,
    left: 0,
    right: 0,
    height: "35%",
    backgroundColor: "#030712",
    opacity: 0.9,
  },
  gridLineH: {
    position: "absolute",
    top: "18%",
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: LANDING_COLORS.gridBright,
  },
  gridLineH2: {
    position: "absolute",
    top: "62%",
    left: 0,
    right: 0,
    height: 1,
    backgroundColor: LANDING_COLORS.grid,
  },
  gridLineV: {
    position: "absolute",
    top: 0,
    bottom: 0,
    left: "50%",
    width: 1,
    backgroundColor: LANDING_COLORS.grid,
  },
  glowOrbCyan: {
    position: "absolute",
    top: -100,
    alignSelf: "center",
    width: 320,
    height: 320,
    borderRadius: 160,
    backgroundColor: "#0284c728",
  },
  glowOrbViolet: {
    position: "absolute",
    bottom: 80,
    right: -40,
    width: 200,
    height: 200,
    borderRadius: 100,
    backgroundColor: "#6366f122",
  },
  scroll: {
    flexGrow: 1,
    justifyContent: "space-between",
    zIndex: 2,
  },
  header: {
    alignItems: "center",
    marginBottom: isCompact ? 8 : 12,
  },
  subtitle: {
    fontSize: isCompact ? 13 : 14,
    color: LANDING_COLORS.subtitle,
    textAlign: "center",
    marginTop: 14,
    lineHeight: 22,
    maxWidth: 340,
    paddingHorizontal: 8,
    fontWeight: "500",
  },
  badge: {
    flexDirection: "row",
    alignItems: "center",
    marginTop: isCompact ? 16 : 22,
    paddingHorizontal: 16,
    paddingVertical: 9,
    borderRadius: 999,
    backgroundColor: LANDING_COLORS.badgeBg,
    borderWidth: 1.5,
    borderColor: LANDING_COLORS.badgeBorder,
  },
  badgeDot: {
    width: 9,
    height: 9,
    borderRadius: 5,
    backgroundColor: LANDING_COLORS.badgeGreen,
    marginRight: 9,
    shadowColor: LANDING_COLORS.badgeGreen,
    shadowOpacity: 0.8,
    shadowRadius: 6,
    elevation: 4,
  },
  badgeText: {
    color: LANDING_COLORS.badgeGreen,
    fontSize: 12,
    fontWeight: "800",
    letterSpacing: 0.8,
  },
  actions: {
    marginTop: isCompact ? 28 : 40,
    gap: 16,
    zIndex: 10,
    position: "relative",
  },
  actionsCompact: {
    marginTop: 22,
    gap: 14,
  },
});
