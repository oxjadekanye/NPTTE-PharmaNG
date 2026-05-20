/**
 * Phase 24 — operational QA simulations (regulator-authenticated pilot APIs + local alerts).
 */
import { apiRequest } from "@/services/api-client";
import { showLocalOperationalAlert } from "@/services/push-orchestration";
import { useOperationalToast } from "@/store/operational-toast-store";

export type SimulationType =
  | "counterfeit_detection"
  | "recall_event"
  | "customs_seizure"
  | "pharmacy_fraud"
  | "shortage_escalation"
  | "enforcement_assignment";

const LABELS: Record<SimulationType, string> = {
  counterfeit_detection: "Simulated counterfeit detection",
  recall_event: "Simulated national recall",
  customs_seizure: "Simulated customs seizure",
  pharmacy_fraud: "Simulated pharmacy fraud alert",
  shortage_escalation: "Simulated shortage escalation",
  enforcement_assignment: "Simulated enforcement assignment",
};

export async function runOperationalSimulation(type: SimulationType) {
  const label = LABELS[type];
  useOperationalToast.getState().show(`Running: ${label}`, "info");

  if (type === "recall_event" || type === "enforcement_assignment" || type === "customs_seizure") {
    const res = await apiRequest<Record<string, unknown>>("/pilot/demo-control/", {
      method: "POST",
      body: JSON.stringify({ action: "seed_incident" }),
    });
    if (res.success) {
      useOperationalToast.getState().show(`${label} — backend incident seeded`, "success");
      await showLocalOperationalAlert("NPTTE QA simulation", label);
      return { ok: true, data: res.data };
    }
  }

  if (type === "counterfeit_detection" || type === "pharmacy_fraud") {
    const res = await apiRequest<Record<string, unknown>>("/pilot/demo-control/", {
      method: "POST",
      body: JSON.stringify({ action: "seed_products" }),
    });
    if (res.success) {
      useOperationalToast.getState().show(`${label} — demo products seeded`, "success");
      await showLocalOperationalAlert("NPTTE QA simulation", label);
      return { ok: true, data: res.data };
    }
  }

  await showLocalOperationalAlert("NPTTE QA simulation", label);
  useOperationalToast.getState().show(`${label} (local notification)`, "success");
  return { ok: true, local: true };
}

export function listSimulations(): { type: SimulationType; label: string }[] {
  return (Object.keys(LABELS) as SimulationType[]).map((type) => ({
    type,
    label: LABELS[type],
  }));
}
