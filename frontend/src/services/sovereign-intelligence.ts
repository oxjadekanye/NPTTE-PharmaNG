import { apiRequest } from "./api-client";

export async function fetchNationalIntelligence() {
  return apiRequest<Record<string, unknown>>("/intelligence/national/");
}

export async function fetchSerialRiskScore(serial_number: string) {
  return apiRequest<Record<string, unknown>>(
    `/intelligence/serial-risk/?serial_number=${encodeURIComponent(serial_number)}`
  );
}
