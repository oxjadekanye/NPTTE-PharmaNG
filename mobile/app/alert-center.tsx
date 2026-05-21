import { useCallback, useMemo, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { DetailRow, DetailSheet } from "@/components/operational/DetailSheet";
import { useRealtimeFeed } from "@/hooks/useRealtimeFeed";
import { apiRequest } from "@/services/api-client";
import { enrichAlertDetail, type AlertDetail } from "@/services/alert-details";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";
import { OperationalCard } from "@/components/ui/OperationalCard";

export default function AlertCenterScreen() {
  const { feed, loading, refresh } = useRealtimeFeed("recall_alert,national_alert");
  const [center, setCenter] = useState<{ alerts: unknown[]; unread_count: number } | null>(null);
  const [selected, setSelected] = useState<AlertDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);
  const [detailError, setDetailError] = useState<string | null>(null);

  const loadCenter = async () => {
    const res = await apiRequest<{ alerts: unknown[]; unread_count: number }>("/alerts/center/");
    if (res.success && res.data) setCenter(res.data);
  };

  const rows = useMemo(() => {
    const merged = [...(center?.alerts ?? []), ...(feed?.alerts ?? [])];
    const seen = new Set<string>();
    return merged.filter((a) => {
      const row = a as { id?: string };
      const id = row.id ?? JSON.stringify(row);
      if (seen.has(id)) return false;
      seen.add(id);
      return true;
    });
  }, [center?.alerts, feed?.alerts]);

  const openDetail = useCallback(async (raw: Record<string, unknown>) => {
    mobileActionLog("alert_detail_opened", String(raw.id ?? "unknown"));
    setDetailLoading(true);
    setDetailError(null);
    setSelected(null);
    try {
      const detail = enrichAlertDetail(raw);
      setSelected(detail);
    } catch (e) {
      setDetailError(e instanceof Error ? e.message : "Could not open alert detail");
    } finally {
      setDetailLoading(false);
    }
  }, []);

  return (
    <ScreenShell title="Alert center" subtitle="National operational notifications">
      <Pressable style={styles.btn} onPress={() => void Promise.all([refresh(), loadCenter()])}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Refresh alerts</Text>
        )}
      </Pressable>
      <Text style={styles.meta}>
        Feed: {rows.length} items · polled{" "}
        {feed?.polled_at ? new Date(feed.polled_at).toLocaleTimeString() : "—"}
      </Text>
      {rows.map((a, i) => {
        const row = a as Record<string, unknown>;
        const preview = enrichAlertDetail(row);
        return (
          <Pressable
            key={preview.id ?? i}
            style={styles.row}
            onPress={() => void openDetail(row)}
            accessibilityRole="button"
            accessibilityLabel={`Open alert ${preview.title}`}
          >
            <Text style={styles.title}>{preview.title}</Text>
            <Text style={styles.sub}>
              {preview.severity} · {preview.organisationName}
            </Text>
            <Text style={styles.hint}>Tap for full operational detail →</Text>
          </Pressable>
        );
      })}
      {rows.length === 0 && !loading && (
        <Text style={styles.empty}>No alerts — pull refresh when online</Text>
      )}

      <DetailSheet
        visible={selected !== null || detailLoading || detailError !== null}
        title={selected?.title ?? "Alert detail"}
        subtitle={selected?.severity}
        onClose={() => {
          setSelected(null);
          setDetailError(null);
        }}
        loading={detailLoading}
        error={detailError}
      >
        {selected ? (
          <OperationalCard title="National alert" variant="enforcement">
            <DetailRow label="Severity" value={selected.severity} />
            <DetailRow label="Priority" value={selected.priority} />
            <DetailRow label="Organisation" value={selected.organisationName} />
            <DetailRow label="Full location" value={selected.addressLine} />
            <DetailRow label="City" value={selected.city} />
            <DetailRow label="LGA" value={selected.lga} />
            <DetailRow label="State" value={selected.state} />
            <DetailRow
              label="Time detected"
              value={new Date(selected.detectedAt).toLocaleString()}
            />
            <DetailRow label="Product" value={selected.productName} />
            <DetailRow label="Batch" value={selected.batch} />
            <DetailRow label="Serial" value={selected.serial} />
            <DetailRow label="Risk explanation" value={selected.riskExplanation} />
            <DetailRow label="Recommended action" value={selected.recommendedAction} />
            <DetailRow label="Linked task" value={selected.linkedTaskId} />
            <DetailRow label="Linked investigation" value={selected.linkedInvestigationId} />
            <DetailRow label="Alert type" value={selected.alertType} />
          </OperationalCard>
        ) : null}
      </DetailSheet>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  btn: { backgroundColor: "#0284c7", padding: 12, borderRadius: 8, alignItems: "center", marginBottom: 12 },
  btnText: { color: "#fff", fontWeight: "600" },
  meta: { color: "#94a3b8", fontSize: 11, marginBottom: 12 },
  row: {
    padding: 14,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
    backgroundColor: "#0f172a",
    borderRadius: 8,
    marginBottom: 8,
  },
  title: { color: "#f8fafc", fontWeight: "600", fontSize: 15 },
  sub: { color: "#94a3b8", fontSize: 12, marginTop: 4 },
  hint: { color: "#38bdf8", fontSize: 10, marginTop: 6 },
  empty: { color: "#64748b", textAlign: "center", marginTop: 24 },
});
