import { router } from "expo-router";
import { CITIZEN_ROUTES, pushCitizenRoute } from "@/services/citizen-navigation";
import { landingLog, openStaffLogin } from "@/navigation/staff-login-intent";
import { useEffect, useRef } from "react";
import { useQaMode } from "@/store/qa-mode-store";
import { useLandingIntent } from "@/store/landing-intent-store";
import { useNavigationStore } from "@/store/navigation-store";
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

type ActionVariant = "primary" | "staff" | "accent" | "alert";

type ActionProps = {
  href: string;
  label: string;
  variant: ActionVariant;
  delay: number;
  slide: Animated.Value;
  publicFlow?: boolean;
  accessibilityLabel?: string;
};

function LandingAction({
  href,
  label,
  variant,
  delay,
  slide,
  publicFlow,
  accessibilityLabel,
}: ActionProps) {
  const setBypassAutoRedirect = useLandingIntent((s) => s.setBypassAutoRedirect);
  const opacity = useRef(new Animated.Value(0)).current;
  const pressScale = useRef(new Animated.Value(1)).current;

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
      : variant === "staff"
        ? styles.btnStaff
        : variant === "accent"
          ? styles.btnAccent
          : styles.btnAlert;

  const textStyle =
    variant === "staff" ? styles.btnTextStaff : styles.btnTextPrimary;

  const animatePressIn = () => {
    Animated.spring(pressScale, { toValue: 0.97, useNativeDriver: true, speed: 40, bounciness: 0 }).start();
  };

  const animatePressOut = () => {
    Animated.spring(pressScale, { toValue: 1, useNativeDriver: true, speed: 40, bounciness: 4 }).start();
  };

  return (
    <Animated.View
      style={{ opacity, transform: [{ translateY: slide }, { scale: pressScale }] }}
      pointerEvents="box-none"
    >
      <Pressable
        style={({ pressed }) => [variantStyle, pressed && styles.btnPressed]}
        pointerEvents="auto"
        accessibilityRole="button"
        accessibilityLabel={accessibilityLabel ?? label}
        onPressIn={animatePressIn}
        onPressOut={animatePressOut}
        onPress={() => {
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
        }}
      >
        <Text style={textStyle}>{label}</Text>
      </Pressable>
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
        <View style={styles.gridLineH} pointerEvents="none" />
        <View style={styles.gridLineV} pointerEvents="none" />
        <View style={styles.glowOrb} pointerEvents="none" />
      </View>
      <ScrollView
        contentContainerStyle={[
          styles.scroll,
          { paddingBottom: bottomPad + 12, paddingHorizontal: isCompact ? 20 : 24 },
        ]}
        showsVerticalScrollIndicator={false}
        bounces={false}
        keyboardShouldPersistTaps="handled"
      >
        <Animated.View
          style={{
            opacity: headerFade,
            transform: [{ translateY: headerSlide }],
            alignItems: "center",
          }}
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
            <NptteLogoMark width={isCompact ? 220 : 260} />
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
          <LandingAction
            href="/citizen"
            label="Citizen Verification"
            variant="primary"
            delay={180}
            slide={actionsSlide}
            publicFlow
            accessibilityLabel="Open citizen verification"
          />
          <LandingAction
            href="/login"
            label="Staff Login"
            variant="staff"
            delay={260}
            slide={actionsSlide}
            accessibilityLabel="Open staff login"
          />
          <LandingAction
            href="/citizen/recalls"
            label="Emergency Recall Alerts"
            variant="accent"
            delay={340}
            slide={actionsSlide}
            publicFlow
            accessibilityLabel="View emergency recall alerts"
          />
          <LandingAction
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
  root: { flex: 1, backgroundColor: "#020617" },
  gridBg: {
    ...StyleSheet.absoluteFillObject,
    backgroundColor: "#020617",
    zIndex: 0,
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
    backgroundColor: "#0284c733",
  },
  scroll: { flexGrow: 1, justifyContent: "space-between", zIndex: 1 },
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
  actions: {
    marginTop: 36,
    gap: 14,
    zIndex: 10,
    position: "relative",
    elevation: 10,
  },
  actionsCompact: { marginTop: 24, gap: 12 },
  btnPrimary: {
    backgroundColor: "#0284c7",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#38bdf8",
    shadowColor: "#0284c7",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.45,
    shadowRadius: 12,
    elevation: 10,
  },
  btnStaff: {
    backgroundColor: "#0369a1",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 2,
    borderColor: "#7dd3fc",
    shadowColor: "#0ea5e9",
    shadowOffset: { width: 0, height: 6 },
    shadowOpacity: 0.4,
    shadowRadius: 12,
    elevation: 10,
  },
  btnAccent: {
    backgroundColor: "#1e3a5f",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#38bdf8aa",
    shadowColor: "#38bdf8",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.28,
    shadowRadius: 10,
    elevation: 6,
  },
  btnAlert: {
    backgroundColor: "#991b1b",
    paddingVertical: 16,
    paddingHorizontal: 20,
    borderRadius: 12,
    alignItems: "center",
    borderWidth: 1,
    borderColor: "#fca5a5aa",
    shadowColor: "#ef4444",
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.32,
    shadowRadius: 10,
    elevation: 6,
  },
  btnPressed: { opacity: 0.9 },
  btnTextPrimary: {
    color: "#ffffff",
    fontWeight: "700",
    fontSize: 16,
    letterSpacing: 0.2,
  },
  btnTextStaff: {
    color: "#f8fafc",
    fontWeight: "700",
    fontSize: 16,
    letterSpacing: 0.2,
  },
});
