import { apiRequest } from "./api-client";

export type TraceabilityStory = {
  seeded: boolean;
  message?: string;
  hero_serial?: string;
  demo_serials?: Record<string, string>;
  lifecycle_timeline?: { step: string; label: string; status: string }[];
  custody_chain?: Record<string, unknown>[];
  transactions?: Record<string, unknown>[];
  regulatory_audits?: Record<string, unknown>[];
  recall?: { active: boolean; reason?: string; batch_number?: string };
  suspicious_scan?: { serial: string; note: string };
  verification_scenarios?: {
    label: string;
    serial_number: string;
    in_registry: boolean;
  }[];
  product?: { name: string; brand: string; code: string };
  batch?: Record<string, unknown>;
};

export async function fetchTraceabilityStory() {
  return apiRequest<TraceabilityStory>("/demo/traceability-story/", { auth: false });
}
