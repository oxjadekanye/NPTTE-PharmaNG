import { fetchExplorerContextRoute } from "@/services/explorer";
import type { ExplorerOpenPayload } from "@/store/explorer-drawer-store";

/** Open drawer with true entity resolution from dashboard context keys. */
export async function openExplorerFromContext(
  openDrawer: (target: ExplorerOpenPayload) => void,
  contextKey: string,
  title?: string
) {
  const res = await fetchExplorerContextRoute(contextKey);
  if (res.success && res.data) {
    const d = res.data as { entity_type: string; entity_id: string; title?: string };
    openDrawer({
      entityType: d.entity_type,
      entityId: d.entity_id,
      title: title ?? d.title,
    });
    return;
  }
  openDrawer({
    entityType: "national_risk",
    entityId: "national-risk-current",
    title: title ?? contextKey,
  });
}

/** Resolve streambus / live event payload to explorer drawer target. */
export function openExplorerFromStreamEvent(
  openDrawer: (target: ExplorerOpenPayload) => void,
  payload: Record<string, unknown> | undefined,
  fallbackTitle?: string
) {
  const p = payload ?? {};
  const target = (p.explorer_target as Record<string, unknown>) ?? {};
  const entityType = String(
    p.explorer_entity_type ?? target.entity_type ?? target.entityType ?? ""
  );
  const entityId = String(p.explorer_entity_id ?? target.entity_id ?? target.entityId ?? "");
  if (entityType && entityId) {
    openDrawer({
      entityType,
      entityId,
      title: fallbackTitle ?? String(p.title ?? p.event_type ?? "Live event"),
    });
    return true;
  }
  return false;
}

export async function openExplorerTarget(
  openDrawer: (target: ExplorerOpenPayload) => void,
  target: {
    title?: string;
    explorer?: { entityType: string; entityId: string };
    context?: string;
  }
) {
  if (target.explorer?.entityType && target.explorer?.entityId) {
    openDrawer({ ...target.explorer, title: target.title });
    return;
  }
  if (target.context) {
    await openExplorerFromContext(openDrawer, target.context, target.title);
  }
}
