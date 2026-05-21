/** Phase 11 — grouped national command navigation (additive). */

export type NavItem = { href: string; label: string };

export type NavSection = { title: string; items: NavItem[] };

export const COMMAND_NAV_SECTIONS: NavSection[] = [
  {
    title: "Command",
    items: [
      { href: "/regulator", label: "Overview" },
      { href: "/command-center", label: "Command Center" },
      { href: "/regulator/intelligence", label: "Sovereign Intelligence" },
      { href: "/regulator/medicines", label: "Medicine intelligence" },
      { href: "/regulator/manufacturers", label: "Manufacturers" },
      { href: "/regulator/supply-chain", label: "Supply chain" },
      { href: "/command-center/recall-orchestration", label: "Recall orchestration" },
      { href: "/executive/crisis-mode", label: "Crisis mode" },
      { href: "/regulator/analytics", label: "National analytics" },
      { href: "/regulator/enforcement", label: "Enforcement" },
      { href: "/regulator/explorer", label: "Drill-down explorer" },
      { href: "/regulator/map", label: "National map" },
      { href: "/command-room", label: "Command room" },
      { href: "/regulator/regions", label: "Regional commands" },
      { href: "/executive", label: "Executive Mode" },
      { href: "/regulator/pilot-readiness", label: "Pilot Readiness" },
      { href: "/pilot", label: "Pilot Presentation" },
    ],
  },
  {
    title: "Operations",
    items: [
      { href: "/regulator/tasks", label: "Operational tasks" },
      { href: "/regulator/alert-center", label: "Alert center" },
      { href: "/regulator/traceability", label: "Traceability" },
      { href: "/regulator/live-demo", label: "Live Demo" },
      { href: "/regulator/serialization", label: "Serialization" },
      { href: "/regulator/custody", label: "Custody Ledger" },
      { href: "/command-center/threat-map", label: "Threat Map" },
      { href: "/command-center/incidents", label: "Incidents" },
      { href: "/command-center/recalls", label: "Recalls" },
      { href: "/emergency-ops", label: "Emergency Ops" },
    ],
  },
  {
    title: "Ecosystem",
    items: [
      { href: "/manufacturer", label: "Manufacturer" },
      { href: "/pharmacy", label: "Pharmacy" },
      { href: "/pharmacy/inventory", label: "Pharmacy inventory" },
      { href: "/warehouse", label: "Warehouse" },
      { href: "/customs", label: "Customs" },
      { href: "/distributor", label: "Distributor" },
      { href: "/hospital", label: "Hospital" },
      { href: "/citizen", label: "Citizen Verify" },
    ],
  },
  {
    title: "Governance",
    items: [
      { href: "/regulator/onboarding", label: "Onboarding" },
      { href: "/regulator/tenant-approvals", label: "Tenant approvals" },
      { href: "/regulator/demo-control", label: "Demo Control" },
      { href: "/regulator/api-readiness", label: "API Readiness" },
      { href: "/regulator/docs", label: "Documentation" },
      { href: "/regulator/audit", label: "Audit & Security" },
      { href: "/developer", label: "Developer API" },
      { href: "/regulator/integrations", label: "Integrations" },
    ],
  },
];
