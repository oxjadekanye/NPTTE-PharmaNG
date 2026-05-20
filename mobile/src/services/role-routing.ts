export type MobileRole =
  | "citizen"
  | "pharmacy"
  | "regulator"
  | "customs"
  | "warehouse"
  | "executive";

/** Ministerial / national command roles → executive mobile home */
const EXECUTIVE_CODES = new Set(["FMOH_ADMIN", "NATIONAL_REGULATOR"]);

/** Field regulator & agency admin roles → regulator mobile home */
const REGULATOR_CODES = new Set([
  "SUPER_ADMIN",
  "NAFDAC_ADMIN",
  "NDLEA_ADMIN",
  "PCN_ADMIN",
  "NHIA_ADMIN",
  "STATE_REGULATOR",
  "AUDITOR",
]);

const CUSTOMS_CODES = new Set(["CUSTOMS_ADMIN"]);

const WAREHOUSE_CODES = new Set([
  "WAREHOUSE_MANAGER",
  "WAREHOUSE_ADMIN",
  "LOGISTICS",
  "DISTRIBUTOR",
  "DISTRIBUTOR_ADMIN",
]);

const PHARMACY_CODES = new Set([
  "PHARMACY_ADMIN",
  "PHARMACIST",
  "PHARMACY_OWNER",
  "PHARMACY_STAFF",
]);

export function resolveMobileRole(
  roleCode?: string | null,
  isRegulator?: boolean
): MobileRole | null {
  if (!roleCode) return isRegulator ? "regulator" : null;
  const code = roleCode.toUpperCase();
  if (code === "PATIENT") return "citizen";
  if (EXECUTIVE_CODES.has(code)) return "executive";
  if (REGULATOR_CODES.has(code) || isRegulator) return "regulator";
  if (CUSTOMS_CODES.has(code)) return "customs";
  if (WAREHOUSE_CODES.has(code)) return "warehouse";
  if (PHARMACY_CODES.has(code)) return "pharmacy";
  return null;
}

export type MobileHomePath =
  | "/citizen"
  | "/pharmacy"
  | "/regulator"
  | "/customs"
  | "/warehouse"
  | "/executive"
  | "/login";

export function mobileHomePath(role: MobileRole): MobileHomePath {
  switch (role) {
    case "citizen":
      return "/citizen";
    case "pharmacy":
      return "/pharmacy";
    case "regulator":
      return "/regulator";
    case "customs":
      return "/customs";
    case "warehouse":
      return "/warehouse";
    case "executive":
      return "/executive";
    default:
      return "/login";
  }
}
