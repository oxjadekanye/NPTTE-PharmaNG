import { useCallback, useState } from "react";
import * as Location from "expo-location";
import { ingestScan, type ScanIngestResult, type ScanIngestPayload, type ScanType } from "@/services/scanning";
import { useOfflineQueue } from "@/store/offline-queue";
import { useNetwork } from "@/hooks/useNetwork";

export function useScanSubmit(scanType: ScanType, actorRole: string) {
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<ScanIngestResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const { online } = useNetwork();
  const enqueue = useOfflineQueue((s) => s.enqueue);
  const ensureDeviceId = useOfflineQueue((s) => s.ensureDeviceId);

  const submit = useCallback(
    async (serial: string) => {
      const trimmed = serial.trim();
      if (!trimmed) return;
      setLoading(true);
      setError(null);
      const deviceId = ensureDeviceId();
      let lat: number | undefined;
      let lng: number | undefined;
      try {
        const { status } = await Location.requestForegroundPermissionsAsync();
        if (status === "granted") {
          const loc = await Location.getCurrentPositionAsync({ accuracy: Location.Accuracy.Balanced });
          lat = loc.coords.latitude;
          lng = loc.coords.longitude;
        }
      } catch {
        /* optional */
      }

      const payload: ScanIngestPayload = {
        serial_number: trimmed,
        scan_type: scanType,
        actor_role: actorRole,
        device_id: deviceId,
        latitude: lat,
        longitude: lng,
      };

      if (!online && scanType !== "citizen_verify") {
        enqueue({ ...payload, offline_timestamp: new Date().toISOString() });
        setResult({
          id: "local",
          serial_number: trimmed,
          scan_type: scanType,
          actor_role: actorRole,
          outcome_label: "queued",
          sync_status: "pending",
          risk_score: 0,
          created_at: new Date().toISOString(),
          result: {},
          alerts: {
            recall_alert: false,
            suspicious_scan_alert: false,
            counterfeit_warning: false,
            failed_sync_warning: false,
          },
        });
        setLoading(false);
        return;
      }

      const res = await ingestScan(payload);
      setLoading(false);
      if (!res.success || !res.data) {
        setError(res.message || "Scan failed");
        return;
      }
      setResult(res.data);
    },
    [scanType, actorRole, online, enqueue, ensureDeviceId]
  );

  return { submit, loading, result, error, clear: () => { setResult(null); setError(null); } };
}
