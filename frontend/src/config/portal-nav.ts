export type PortalNavItem = { href: string; label: string };

/** Shared navigation across national ecosystem portals (additive routes). */
export const ECOSYSTEM_HUB_NAV: PortalNavItem[] = [
  { href: "/manufacturer", label: "Manufacturer" },
  { href: "/pharmacy", label: "Pharmacy" },
  { href: "/warehouse", label: "Warehouse" },
  { href: "/customs", label: "Customs" },
  { href: "/distributor", label: "Distributor" },
  { href: "/hospital", label: "Hospital" },
  { href: "/ert", label: "Emergency Response" },
  { href: "/executive", label: "Executive" },
  { href: "/command-center/recalls", label: "Recall Center" },
];
