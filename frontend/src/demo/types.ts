/** DEMO/SIMULATED intelligence types — not production operational data. */

export type NationalStatus = "stable" | "warning" | "critical";

export type DemoSeverity = "low" | "medium" | "high" | "critical";

export interface DemoStateRisk {
  state: string;
  code: string;
  riskScore: number;
  counterfeitCount: number;
  shortageCount: number;
  pharmacyCount: number;
  lat: number;
  lng: number;
}

export interface DemoHotspot {
  id: string;
  lat: number;
  lng: number;
  intensity: number;
  label: string;
  type: "counterfeit" | "seizure" | "diversion" | "online_pharmacy";
}

/** Phase 9 — sovereign map layer toggles (simulated overlays). */
export type MapIntelLayer = "risk" | "pharmacy_density" | "shortage" | "customs" | "investigations" | "logistics";

export interface DemoWarehouseHub {
  id: string;
  name: string;
  lat: number;
  lng: number;
  throughput: number;
}

export interface DemoIncident {
  id: string;
  code: string;
  title: string;
  category: string;
  severity: DemoSeverity;
  status: "open" | "investigating" | "escalated" | "resolved";
  state: string;
  city: string;
  assignedTo: string;
  agency: string;
  threatScore: number;
  openedAt: string;
  linkedPharmacies: string[];
  linkedBatches: string[];
  linkedSuppliers: string[];
  regulators: string[];
  inspectors: string[];
  timeline: { at: string; event: string }[];
}

export interface DemoFeedEvent {
  id: string;
  at: string;
  type: string;
  message: string;
  severity: DemoSeverity;
}

export interface DemoAuditEntry {
  id: string;
  at: string;
  actor: string;
  role: string;
  action: string;
  entity: string;
  immutable: boolean;
}

export interface DemoBlacklistedBatch {
  batchNumber: string;
  product: string;
  manufacturer: string;
  reason: string;
  listedAt: string;
}

export interface DemoRecall {
  recallNumber: string;
  product: string;
  states: string[];
  severity: DemoSeverity;
}

export interface NationalKpis {
  verificationsToday: number;
  counterfeitDetections: number;
  activeInvestigations: number;
  shortageAlerts: number;
  recallsActive: number;
  fraudAlerts: number;
  customsInterceptions: number;
  warehouseInspections: number;
  scanSuccessRate: number;
  complianceRate: number;
  counterfeitReductionPct: number;
}
