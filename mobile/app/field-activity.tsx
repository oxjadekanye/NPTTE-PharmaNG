import { useCallback, useEffect, useState } from "react";
import { ActivityIndicator, Pressable, StyleSheet, Text, View } from "react-native";
import { ScreenShell } from "@/components/ScreenShell";
import { DetailRow, DetailSheet } from "@/components/operational/DetailSheet";
import { OperationalCard } from "@/components/ui/OperationalCard";
import { fetchMobileAuditTimeline } from "@/services/audit";
import { enrichActivityDetail, type ActivityDetail } from "@/services/activity-details";
import { mobileActionLog } from "@/services/mobile-action-diagnostics";

export default function FieldActivityScreen() {
  const [rows, setRows] = useState<Record<string, unknown>[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [selected, setSelected] = useState<ActivityDetail | null>(null);
  const [detailLoading, setDetailLoading] = useState(false);

  const load = useCallback(async () => {
    setLoading(true);
    setLoadError(null);
    try {
      const r = await fetchMobileAuditTimeline();
      if (r.success && r.data?.timeline) setRows(r.data.timeline);
      else setLoadError(r.message || "Could not load activity");
    } catch (e) {
      setLoadError(e instanceof Error ? e.message : "Load failed");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const openDetail = (raw: Record<string, unknown>) => {
    mobileActionLog("activity_detail_opened", String(raw.id ?? "unknown"));
    setDetailLoading(true);
    setSelected(null);
    try {
      setSelected(enrichActivityDetail(raw));
    } finally {
      setDetailLoading(false);
    }
  };

  return (
    <ScreenShell title="Field activity" subtitle="Mobile operational audit trail">
      <Pressable style={styles.btn} onPress={() => void load()} disabled={loading}>
        {loading ? (
          <ActivityIndicator color="#fff" />
        ) : (
          <Text style={styles.btnText}>Refresh activity</Text>
        )}
      </Pressable>
      {loadError ? <Text style={styles.error}>{loadError}</Text> : null}
      {rows.map((r) => {
        const preview = enrichActivityDetail(r);
        return (
          <Pressable
            key={preview.id}
            style={styles.row}
            onPress={() => openDetail(r)}
            accessibilityRole="button"
            accessibilityLabel={`Open activity ${preview.activityType}`}
          >
            <Text style={styles.type}>{preview.activityType}</Text>
            <Text style={styles.meta}>{new Date(preview.timestamp).toLocaleString()}</Text>
            <Text style={styles.hint}>{preview.organisationName} · Tap for details →</Text>
          </Pressable>
        );
      })}
      {rows.length === 0 && !loading && <Text style={styles.empty}>No activity yet</Text>}

      <DetailSheet
        visible={selected !== null || detailLoading}
        title={selected?.activityType ?? "Activity detail"}
        subtitle={selected ? new Date(selected.timestamp).toLocaleString() : undefined}
        onClose={() => setSelected(null)}
        loading={detailLoading}
      >
        {selected ? (
          <OperationalCard title="Field activity record">
            <DetailRow label="Activity type" value={selected.activityType} />
            <DetailRow label="Officer / staff" value={selected.officerName} />
            <DetailRow label="Organisation" value={selected.organisationName} />
            <DetailRow label="Full location" value={selected.addressLine} />
            <DetailRow label="City" value={selected.city} />
            <DetailRow label="State" value={selected.state} />
            <DetailRow
              label="Timestamp"
              value={new Date(selected.timestamp).toLocaleString()}
            />
            <DetailRow label="Linked scan" value={selected.linkedScanId} />
            <DetailRow label="Linked evidence" value={selected.linkedEvidenceId} />
            <DetailRow label="Linked task" value={selected.linkedTaskId} />
            <DetailRow label="Linked case" value={selected.linkedCaseId} />
            <DetailRow label="Outcome / status" value={selected.outcomeStatus} />
            <DetailRow label="Sync status" value={selected.syncStatus} />
            <DetailRow label="Device" value={selected.deviceId} />
            <DetailRow label="Audit note" value={selected.auditNote} />
          </OperationalCard>
        ) : null}
      </DetailSheet>
    </ScreenShell>
  );
}

const styles = StyleSheet.create({
  btn: { backgroundColor: "#0284c7", padding: 12, borderRadius: 8, alignItems: "center", marginBottom: 12 },
  btnText: { color: "#fff", fontWeight: "600" },
  row: {
    paddingVertical: 12,
    paddingHorizontal: 4,
    borderBottomWidth: 1,
    borderBottomColor: "#1e293b",
    marginBottom: 4,
  },
  type: { color: "#f8fafc", fontWeight: "600" },
  meta: { color: "#94a3b8", fontSize: 11, marginTop: 2 },
  hint: { color: "#38bdf8", fontSize: 10, marginTop: 4 },
  empty: { color: "#64748b" },
  error: { color: "#fbbf24", marginBottom: 8 },
});
