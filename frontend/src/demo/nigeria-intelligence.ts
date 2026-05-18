/**
 * DEMO/SIMULATED national pharmaceutical intelligence for UI presentation.
 * Not live operational data — used when API payloads are sparse or for demonstration.
 */
import type {
  DemoAuditEntry,
  DemoBlacklistedBatch,
  DemoFeedEvent,
  DemoHotspot,
  DemoIncident,
  DemoRecall,
  DemoStateRisk,
  DemoWarehouseHub,
  NationalKpis,
  NationalStatus,
} from "./types";

export const DEMO_LABEL = "DEMO · Simulated intelligence";

export const NATIONAL_KPIS: NationalKpis = {
  verificationsToday: 184_293,
  counterfeitDetections: 347,
  activeInvestigations: 28,
  shortageAlerts: 19,
  recallsActive: 4,
  fraudAlerts: 52,
  customsInterceptions: 11,
  warehouseInspections: 6,
  scanSuccessRate: 94.2,
  complianceRate: 87.6,
  counterfeitReductionPct: 12.4,
};

export const STATE_RISKS: DemoStateRisk[] = [
  { state: "Lagos", code: "LA", riskScore: 78, counterfeitCount: 89, shortageCount: 4, pharmacyCount: 1240, lat: 6.5244, lng: 3.3792 },
  { state: "Kano", code: "KN", riskScore: 71, counterfeitCount: 42, shortageCount: 3, pharmacyCount: 380, lat: 12.0022, lng: 8.592 },
  { state: "Rivers", code: "RI", riskScore: 65, counterfeitCount: 31, shortageCount: 2, pharmacyCount: 290, lat: 4.8156, lng: 7.0498 },
  { state: "FCT", code: "FC", riskScore: 58, counterfeitCount: 24, shortageCount: 1, pharmacyCount: 410, lat: 9.0765, lng: 7.3986 },
  { state: "Oyo", code: "OY", riskScore: 54, counterfeitCount: 19, shortageCount: 2, pharmacyCount: 350, lat: 7.3775, lng: 3.947 },
  { state: "Kaduna", code: "KD", riskScore: 62, counterfeitCount: 28, shortageCount: 2, pharmacyCount: 220, lat: 10.5105, lng: 7.4165 },
  { state: "Anambra", code: "AN", riskScore: 49, counterfeitCount: 15, shortageCount: 1, pharmacyCount: 180, lat: 6.2104, lng: 7.0719 },
  { state: "Enugu", code: "EN", riskScore: 45, counterfeitCount: 12, shortageCount: 1, pharmacyCount: 165, lat: 6.4584, lng: 7.5464 },
];

export const HOTSPOTS: DemoHotspot[] = [
  { id: "h1", lat: 6.45, lng: 3.39, intensity: 92, label: "Lagos Island — counterfeit cluster", type: "counterfeit" },
  { id: "h2", lat: 6.6, lng: 3.35, intensity: 70, label: "Ikeja — illegal online pharmacy reports", type: "online_pharmacy" },
  { id: "h3", lat: 12.0, lng: 8.59, intensity: 85, label: "Kano — seizure at Sabon Gari", type: "seizure" },
  { id: "h4", lat: 4.78, lng: 7.0, intensity: 68, label: "Port Harcourt — diversion alert", type: "diversion" },
  { id: "h5", lat: 9.08, lng: 7.4, intensity: 55, label: "Abuja — unregistered distributor", type: "diversion" },
  { id: "h6", lat: 7.38, lng: 3.95, intensity: 48, label: "Ibadan — batch verification spike", type: "counterfeit" },
];

export const DEMO_INCIDENTS: DemoIncident[] = [
  {
    id: "inc-001",
    code: "NPTTE-INC-2026-0142",
    title: "Counterfeit antimalarial batch — Lagos metro",
    category: "counterfeit",
    severity: "critical",
    status: "investigating",
    state: "Lagos",
    city: "Lagos Island",
    assignedTo: "Insp. Adebayo Okonkwo",
    agency: "NAFDAC Lagos Zonal Office",
    threatScore: 88,
    openedAt: "2026-05-17T06:22:00Z",
    linkedPharmacies: ["Lagos Central Pharmacy Ltd", "Mushin Community Chemist"],
    linkedBatches: ["NG-NPTTE-ARTEMETHER-2026-BLK-0091"],
    linkedSuppliers: ["Gulfline Distributors NG"],
    regulators: ["NAFDAC", "NDLEA"],
    inspectors: ["Insp. Okonkwo", "Insp. Bello"],
    timeline: [
      { at: "06:22", event: "Citizen scan flagged counterfeit — NG-NPTTE serial mismatch" },
      { at: "07:10", event: "Field team dispatched — Lagos Island" },
      { at: "08:45", event: "Sample seized — chain-of-custody initiated" },
    ],
  },
  {
    id: "inc-002",
    code: "NPTTE-INC-2026-0138",
    title: "Cold chain breach — insulin shipment Enugu",
    category: "cold_chain_breach",
    severity: "high",
    status: "escalated",
    state: "Enugu",
    city: "Enugu",
    assignedTo: "Dr. Chioma Eze",
    agency: "FMOH Emergency Medicines Unit",
    threatScore: 72,
    openedAt: "2026-05-16T22:10:00Z",
    linkedPharmacies: ["Enugu Specialist Hospital Pharmacy"],
    linkedBatches: ["B-INSULIN-EN-2026-044"],
    linkedSuppliers: ["MedTrans Logistics NG"],
    regulators: ["NAFDAC", "FMOH"],
    inspectors: ["Insp. Eze", "Insp. Musa"],
    timeline: [
      { at: "22:10", event: "Temperature excursion logged at warehouse checkpoint" },
      { at: "23:00", event: "National alert issued — shortage risk Enugu" },
    ],
  },
  {
    id: "inc-003",
    code: "NPTTE-INC-2026-0135",
    title: "Customs interception — Apapa port",
    category: "smuggling",
    severity: "high",
    status: "open",
    state: "Lagos",
    city: "Apapa",
    assignedTo: "ACG Tunde Williams",
    agency: "Nigeria Customs Service — Area II",
    threatScore: 79,
    openedAt: "2026-05-16T14:00:00Z",
    linkedPharmacies: [],
    linkedBatches: ["IMP-MANIFEST-2026-AP-771"],
    linkedSuppliers: ["Sahel Pharma Imports Ltd"],
    regulators: ["NAFDAC", "Customs"],
    inspectors: ["Insp. Williams", "Insp. Hassan"],
    timeline: [{ at: "14:00", event: "Import manifest risk score 84 — hold notice issued" }],
  },
  {
    id: "inc-004",
    code: "NPTTE-INC-2026-0129",
    title: "Illegal online pharmacy — Kano",
    category: "unregistered_product",
    severity: "medium",
    status: "investigating",
    state: "Kano",
    city: "Kano",
    assignedTo: "PCN Inspector Yusuf Garba",
    agency: "Pharmacy Council of Nigeria",
    threatScore: 61,
    openedAt: "2026-05-15T09:30:00Z",
    linkedPharmacies: ["Kano MedQuick Online (unregistered)"],
    linkedBatches: [],
    linkedSuppliers: [],
    regulators: ["PCN", "NAFDAC"],
    inspectors: ["Insp. Garba"],
    timeline: [{ at: "09:30", event: "Citizen fraud report — 12 linked serials invalid" }],
  },
];

export const BLACKLISTED_BATCHES: DemoBlacklistedBatch[] = [
  {
    batchNumber: "NG-NPTTE-ARTEMETHER-2026-BLK-0091",
    product: "Artemether/Lumefantrine",
    manufacturer: "Lagos Pharma Industries Ltd",
    reason: "Counterfeit cluster — Lagos Island",
    listedAt: "2026-05-17",
  },
  {
    batchNumber: "B-AMOX-2026-FAKE-221",
    product: "Amoxicillin 500mg",
    manufacturer: "Unknown — unregistered",
    reason: "NAFDAC enforcement — Kano seizure",
    listedAt: "2026-05-14",
  },
];

export const ACTIVE_RECALLS: DemoRecall[] = [
  {
    recallNumber: "REC-NG-2026-018",
    product: "Paracetamol 500mg",
    states: ["Lagos", "Ogun", "Oyo"],
    severity: "high",
  },
  {
    recallNumber: "REC-NG-2026-015",
    product: "Pediatric cough syrup",
    states: ["Kano", "Kaduna"],
    severity: "critical",
  },
];

export const INITIAL_FEED: DemoFeedEvent[] = [
  {
    id: "f1",
    at: new Date().toISOString(),
    type: "verification",
    message: "Lagos: 1,240 citizen scans in last hour — 3 counterfeit flags",
    severity: "medium",
  },
  {
    id: "f2",
    at: new Date().toISOString(),
    type: "customs",
    message: "Apapa: Import hold — Sahel Pharma Imports manifest AP-771",
    severity: "high",
  },
  {
    id: "f3",
    at: new Date().toISOString(),
    type: "shortage",
    message: "Enugu: Insulin stock below national watchlist threshold",
    severity: "critical",
  },
];

export const TICKER_MESSAGES = [
  "NAFDAC Lagos: Counterfeit antimalarial investigation active — INC-2026-0142",
  "NCS Apapa: Customs hold on pharmaceutical import manifest AP-771",
  "FMOH: Emergency insulin watch — Enugu cold chain breach",
  "PCN Kano: Illegal online pharmacy under investigation",
  "NPTTE: 184,293 verifications processed nationally (24h rolling — DEMO)",
];

export const AUDIT_LOG: DemoAuditEntry[] = [
  {
    id: "a1",
    at: "2026-05-17T08:45:00Z",
    actor: "nptte_admin",
    role: "NAFDAC_ADMIN",
    action: "regulatory.batch_suspend",
    entity: "product_batch",
    immutable: true,
  },
  {
    id: "a2",
    at: "2026-05-17T07:10:00Z",
    actor: "Insp. Adebayo Okonkwo",
    role: "NAFDAC_ADMIN",
    action: "incident.assign",
    entity: "NPTTE-INC-2026-0142",
    immutable: true,
  },
  {
    id: "a3",
    at: "2026-05-17T06:22:00Z",
    actor: "citizen_portal",
    role: "PUBLIC",
    action: "verification.counterfeit_report",
    entity: "NG-NPTTE-ARTEMETHER-2026-BLK-0091",
    immutable: true,
  },
];

export const CHART_VERIFICATION_TREND = [
  { day: "Mon", scans: 142000, authentic: 134500, flagged: 2100 },
  { day: "Tue", scans: 156000, authentic: 148200, flagged: 2300 },
  { day: "Wed", scans: 168000, authentic: 159800, flagged: 2450 },
  { day: "Thu", scans: 175000, authentic: 166900, flagged: 2600 },
  { day: "Fri", scans: 184293, authentic: 175800, flagged: 2750 },
  { day: "Sat", scans: 121000, authentic: 115400, flagged: 1800 },
  { day: "Sun", scans: 98000, authentic: 93400, flagged: 1500 },
];

export const CHART_FRAUD_TREND = [
  { month: "Jan", cases: 28 },
  { month: "Feb", cases: 34 },
  { month: "Mar", cases: 41 },
  { month: "Apr", cases: 38 },
  { month: "May", cases: 52 },
];

export const CHART_SHORTAGE_FORECAST = [
  { state: "Lagos", current: 72, forecast: 68 },
  { state: "Kano", current: 58, forecast: 45 },
  { state: "Enugu", current: 41, forecast: 28 },
  { state: "Rivers", current: 65, forecast: 62 },
  { state: "FCT", current: 78, forecast: 75 },
];

export const CHART_SUPPLY_FLOW = [
  { stage: "Manufacturer", volume: 4200 },
  { stage: "Distributor", volume: 3900 },
  { stage: "Warehouse", volume: 3600 },
  { stage: "Pharmacy", volume: 3100 },
  { stage: "Patient", volume: 2800 },
];

export function computeNationalStatus(kpis: NationalKpis): NationalStatus {
  if (kpis.recallsActive >= 3 || kpis.shortageAlerts >= 15 || kpis.counterfeitDetections > 400) {
    return "critical";
  }
  if (
    kpis.activeInvestigations >= 20 ||
    kpis.fraudAlerts >= 40 ||
    kpis.shortageAlerts >= 8
  ) {
    return "warning";
  }
  return "stable";
}

export const LOGISTICS_ROUTES = [
  { from: [6.52, 3.38] as [number, number], to: [9.08, 7.4] as [number, number], label: "Lagos → Abuja" },
  { from: [9.08, 7.4] as [number, number], to: [12.0, 8.59] as [number, number], label: "Abuja → Kano" },
];

/** Phase 9 — warehouse hubs for map / logistics portal (simulated). */
export const WAREHOUSE_HUBS: DemoWarehouseHub[] = [
  { id: "wh-1", name: "Lagos Pharma Bond — Apapa", lat: 6.44, lng: 3.35, throughput: 920 },
  { id: "wh-2", name: "Abuja National Cold Hub", lat: 9.05, lng: 7.49, throughput: 540 },
  { id: "wh-3", name: "Kano Northern Distribution", lat: 11.99, lng: 8.52, throughput: 610 },
  { id: "wh-4", name: "Port Harcourt South Hub", lat: 4.77, lng: 7.02, throughput: 480 },
];

/** Customs / border checkpoints (simulated markers). */
export const CUSTOMS_MARKERS: DemoHotspot[] = [
  { id: "cs-1", lat: 6.44, lng: 3.35, intensity: 88, label: "Apapa — pharmaceutical manifest lane", type: "seizure" },
  { id: "cs-2", lat: 13.06, lng: 5.24, intensity: 72, label: "Sokoto — trans-Sahel corridor watch", type: "diversion" },
  { id: "cs-3", lat: 6.32, lng: 5.61, intensity: 65, label: "Seme border — import authentication queue", type: "seizure" },
];

/** Active investigation zones (pulse). */
export const INVESTIGATION_ZONES: DemoHotspot[] = [
  { id: "inv-1", lat: 6.45, lng: 3.39, intensity: 91, label: "Task force zone — Lagos Island INC-0142", type: "counterfeit" },
  { id: "inv-2", lat: 12.0, lng: 8.59, intensity: 74, label: "PCN / NAFDAC joint sweep — Kano metro", type: "online_pharmacy" },
];
