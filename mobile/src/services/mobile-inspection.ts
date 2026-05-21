export type InspectionSectionId = "site" | "product" | "compliance";

export type InspectionSection = {
  id: InspectionSectionId;
  title: string;
  items: string[];
};

export const INSPECTION_SECTIONS: InspectionSection[] = [
  {
    id: "site",
    title: "Site verification",
    items: ["Registration displayed", "Storage conditions", "Staff interviewed"],
  },
  {
    id: "product",
    title: "Product verification",
    items: ["Serial samples scanned", "Batch records reviewed", "Expiry checks"],
  },
  {
    id: "compliance",
    title: "Compliance",
    items: ["Cold-chain logs", "Custody documentation", "Recall acknowledgement"],
  },
];

export function inspectionItemKey(sectionId: InspectionSectionId, item: string) {
  return `${sectionId}:${item}`;
}

export function computeInspectionScore(checks: Record<string, boolean>) {
  const total = INSPECTION_SECTIONS.reduce((n, s) => n + s.items.length, 0);
  const done = Object.values(checks).filter(Boolean).length;
  return total ? Math.round((done / total) * 100) : 0;
}

export function sectionPassed(
  sectionId: InspectionSectionId,
  checks: Record<string, boolean>
): boolean {
  const section = INSPECTION_SECTIONS.find((s) => s.id === sectionId);
  if (!section) return false;
  return section.items.every((item) => checks[inspectionItemKey(sectionId, item)]);
}

export function failedInspectionItems(checks: Record<string, boolean>): string[] {
  const failed: string[] = [];
  for (const sec of INSPECTION_SECTIONS) {
    for (const item of sec.items) {
      const key = inspectionItemKey(sec.id, item);
      if (!checks[key]) failed.push(`${sec.title}: ${item}`);
    }
  }
  return failed;
}

export function buildInspectionContext(
  checks: Record<string, boolean>,
  evidenceCount: number,
  organisationHint?: string
) {
  return {
    site_passed: sectionPassed("site", checks),
    product_passed: sectionPassed("product", checks),
    compliance_passed: sectionPassed("compliance", checks),
    failed_items: failedInspectionItems(checks),
    evidence_count: evidenceCount,
    compliance_score: computeInspectionScore(checks),
    inspection_context: organisationHint ?? "Field inspection — mobile guided workflow",
  };
}
