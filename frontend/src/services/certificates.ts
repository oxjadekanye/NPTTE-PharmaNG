import { apiRequest } from "./api-client";

export async function fetchCertificates() {
  return apiRequest<{ certificates: unknown[] }>("/certificates/");
}

export async function verifyCertificate(qr_verification_code: string) {
  return apiRequest<Record<string, unknown>>("/certificates/verify/", {
    method: "POST",
    body: JSON.stringify({ qr_verification_code }),
    auth: false,
  });
}
