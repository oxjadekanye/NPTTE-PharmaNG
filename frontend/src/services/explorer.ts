import { apiRequest } from "./api-client";

export type ExplorerContextRoute = {
  entity_type: string;
  entity_id: string;
  title?: string;
  subtitle?: string;
  resolved?: boolean;
};

export type ExplorerOverview = {
  entity_type: string;
  entity_id: string;
  summary: Record<string, unknown>;
  confidence_score?: number;
  tenant_visibility?: string;
  record_count?: number;
  record_preview?: Record<string, unknown>[];
  recommended_actions?: string[];
  risk_score?: number;
  risk_status?: string;
};

export type PaginatedSlice<T = unknown> = {
  items: T[];
  page: number;
  page_size: number;
  total: number;
  has_more: boolean;
};

export function fetchExplorerContextRoute(context: string) {
  return apiRequest<ExplorerContextRoute>(`/explorer/context-route/?context=${encodeURIComponent(context)}`);
}

export function fetchExplorerContextBundle(context: string, page = 1, pageSize = 25) {
  return apiRequest<Record<string, unknown>>(
    `/explorer/context-bundle/?context=${encodeURIComponent(context)}&page=${page}&page_size=${pageSize}`
  );
}

export function fetchExplorerStaff() {
  return apiRequest<{ staff: { id: string; full_name: string; role_title?: string; team?: string }[] }>(
    "/explorer/staff/"
  );
}

export function fetchExplorerOverview(entityType: string, entityId: string) {
  return apiRequest<ExplorerOverview>(
    `/explorer/overview/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/`
  );
}

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

export function fetchExplorerTimeline(entityType: string, entityId: string, page = 1) {
  return apiRequest<{ timeline: PaginatedSlice }>(
    `/explorer/timeline/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/?page=${page}`
  );
}

export function fetchExplorerEvidence(entityType: string, entityId: string, page = 1) {
  return apiRequest<{ evidence: PaginatedSlice }>(
    `/explorer/evidence/${encodeURIComponent(entityType)}/${encodeURIComponent(entityId)}/?page=${page}`
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
