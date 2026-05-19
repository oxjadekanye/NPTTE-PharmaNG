import { Link, router } from "expo-router";
import { useEffect } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { SafeAreaView } from "react-native-safe-area-context";
import { mobileHomePath } from "@/lib/role-routing";
import { useAuthStore } from "@/store/auth-store";

export default function WelcomeScreen() {
  const { loading, mobileRole, hydrate } = useAuthStore();

  useEffect(() => {
    void hydrate().then((role) => {
      if (role) router.replace(mobileHomePath(role));
    });
  }, [hydrate]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#38bdf8" />
      </View>
    );
  }

  if (mobileRole) return null;

  return (
    <SafeAreaView style={styles.safe}>
      <View style={styles.hero}>
        <Text style={styles.brand}>NPTTE PharmaNG</Text>
        <Text style={styles.tag}>National pharmaceutical traceability — mobile field operations</Text>
      </View>
      <Link href="/citizen" asChild>
        <Pressable style={styles.primary}>
          <Text style={styles.primaryText}>Citizen verify (no login)</Text>
        </Pressable>
      </Link>
      <Link href="/login" asChild>
        <Pressable style={styles.secondary}>
          <Text style={styles.secondaryText}>Staff login</Text>
        </Pressable>
      </Link>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  safe: { flex: 1, backgroundColor: "#020617", padding: 24, justifyContent: "center" },
  center: { flex: 1, justifyContent: "center", alignItems: "center", backgroundColor: "#020617" },
  hero: { marginBottom: 32 },
  brand: { fontSize: 28, fontWeight: "700", color: "#f8fafc" },
  tag: { fontSize: 14, color: "#94a3b8", marginTop: 8 },
  primary: {
    backgroundColor: "#0284c7",
    padding: 16,
    borderRadius: 10,
    alignItems: "center",
    marginBottom: 12,
  },
  primaryText: { color: "#fff", fontWeight: "600", fontSize: 16 },
  secondary: {
    borderWidth: 1,
    borderColor: "#334155",
    padding: 16,
    borderRadius: 10,
    alignItems: "center",
  },
  secondaryText: { color: "#38bdf8", fontWeight: "600" },
});
