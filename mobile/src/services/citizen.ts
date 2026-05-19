import { apiRequest } from "@/services/api-client";

export async function publicVerify(payload: {
  serial_number?: string;
  qr_token?: string;
  barcode?: string;
}) {
  return apiRequest<Record<string, unknown>>("/public/verify/", {
    method: "POST",
    body: JSON.stringify(payload),
    auth: false,
  });
}

export async function reportCounterfeit(payload: {
  description: string;
  serial_number?: string;
  pharmacy_name?: string;
  state?: string;
}) {
  return apiRequest("/public/report-counterfeit/", {
    method: "POST",
    body: JSON.stringify(payload),
    auth: false,
  });
}

export async function fetchPublicRecalls() {
  return apiRequest<{ recalls: unknown[] }>("/public/recalls/", { auth: false });
}
