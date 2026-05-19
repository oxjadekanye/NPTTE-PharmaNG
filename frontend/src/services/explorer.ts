import { apiRequest } from "./api-client";

export function fetchExplorerResolve(entityType: string, entityId: string) {
  const q = `?type=${encodeURIComponent(entityType)}&id=${encodeURIComponent(entityId)}`;
  return apiRequest<Record<string, unknown>>(`/explorer/resolve/${q}`);
}

export function fetchExplorerDetail(entityType: string, entityId: string) {
  return apiRequest<Record<string, unknown>>(
    `/explorer/detail/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/`
  );
}

export function fetchExplorerRelated(entityType: string, entityId: string) {
  return apiRequest<{ related_entities: Record<string, unknown> }>(
    `/explorer/related/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/`
  );
}

export function fetchExplorerTimeline(entityType: string, entityId: string) {
  return apiRequest<{ timeline: unknown[] }>(
    `/explorer/timeline/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/`
  );
}

export function fetchExplorerEvidence(entityType: string, entityId: string) {
  return apiRequest<{ evidence: unknown[] }>(
    `/explorer/evidence/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/`
  );
}

export function fetchExplorerActions(entityType: string, entityId: string) {
  return apiRequest<{ actions: { id: string; label: string; requires_confirm?: boolean }[] }>(
    `/explorer/actions/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/`
  );
}

export function fetchExplorerRiskBreakdown(entityType: string, entityId: string) {
  return apiRequest<Record<string, unknown>>(
    `/explorer/risk-breakdown/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/`
  );
}

export function executeExplorerAction(
  entityType: string,
  entityId: string,
  body: Record<string, unknown>
) {
  return apiRequest<Record<string, unknown>>(
    `/explorer/actions/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/execute/`,
    { method: "POST", body: JSON.stringify(body) }
  );
}
