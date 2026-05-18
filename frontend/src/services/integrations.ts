import { apiRequest } from "./api-client";

export async function fetchIntegrationHealth() {
  return apiRequest<{
    providers: unknown[];
    persisted_health: unknown[];
    notification_queue: { pending_exports: number };
  }>("/integrations/health/");
}

export async function fetchWebhookSubscriptions() {
  return apiRequest<{ subscriptions: unknown[] }>("/integrations/webhooks/");
}

export async function fetchWebhookDeliveries() {
  return apiRequest<{ deliveries: unknown[] }>("/integrations/webhooks/deliveries/");
}

export async function fetchExportJobs() {
  return apiRequest<{ exports: unknown[] }>("/integrations/exports/");
}

export async function createExportJob(body: Record<string, string>) {
  return apiRequest("/integrations/exports/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchIntegrationApiKeys() {
  return apiRequest<{ keys: unknown[] }>("/integrations/keys/");
}

export async function createIntegrationApiKey(body: Record<string, unknown>) {
  return apiRequest("/integrations/keys/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchExternalConnectors() {
  return apiRequest<{ connectors: unknown[] }>("/integrations/connectors/");
}

export async function generatePdf(body: Record<string, string>) {
  return apiRequest<{ storage_key: string }>("/integrations/pdf/generate/", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export async function fetchAnalyticsSnapshots() {
  return apiRequest<{ snapshots: unknown[] }>("/integrations/analytics/");
}
