/** In-app pilot documentation (Phase 11). */

export type DocGuide = { id: string; title: string; sections: { heading: string; body: string }[] };

export const PILOT_GUIDES: DocGuide[] = [
  {
    id: "regulator",
    title: "Regulator demo guide",
    sections: [
      { heading: "Login", body: "Use NAFDAC regulator credentials on /login." },
      { heading: "Command Center", body: "Review live overview, threat map, and active incidents." },
      { heading: "Traceability", body: "Approve batches, run verification lookup, inspect movement timeline." },
      { heading: "Executive", body: "Present ministerial KPIs and national AI snapshot to leadership." },
    ],
  },
  {
    id: "pharmacy",
    title: "Pharmacy workflow guide",
    sections: [
      { heading: "Portal", body: "Open /pharmacy for inventory, dispense, and alert modules." },
      { heading: "Receive & dispense", body: "Scan serials on receipt; verify before dispense." },
    ],
  },
  {
    id: "manufacturer",
    title: "Manufacturer workflow guide",
    sections: [
      { heading: "Portal", body: "Open /manufacturer for batch production and serialization queue." },
      { heading: "Regulatory", body: "Submit batches via traceability console for NAFDAC approval." },
    ],
  },
  {
    id: "citizen",
    title: "Citizen verification guide",
    sections: [
      { heading: "Public URL", body: "Share /citizen — no login required." },
      { heading: "Outcomes", body: "Authentic, suspicious, recalled, expired, duplicate scan states." },
    ],
  },
  {
    id: "traceability",
    title: "Traceability workflow guide",
    sections: [
      { heading: "National ledger", body: "Immutable transactions at /regulator/traceability." },
      { heading: "Custody", body: "Per-serial chain at /regulator/custody." },
    ],
  },
  {
    id: "recall",
    title: "Recall workflow guide",
    sections: [
      { heading: "Recall center", body: "/command-center/recalls for propagation and pharmacy ACK." },
    ],
  },
  {
    id: "emergency",
    title: "Emergency response guide",
    sections: [
      { heading: "ERT", body: "/ert and /emergency-ops for mobilisation playbooks." },
    ],
  },
];
