import { apiRequest } from "./api-client";

export async function fetchDeveloperOverview() {
  return apiRequest<Record<string, unknown>>("/developer/overview/");
}

export async function fetchDeveloperKeys() {
  return apiRequest<{ keys: unknown[] }>("/developer/keys/");
}
