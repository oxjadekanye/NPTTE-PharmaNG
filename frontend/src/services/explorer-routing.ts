import { fetchExplorerContextRoute } from "@/services/explorer";
import { resolveContextTarget } from "@/services/explorer-context-map";
import { perfMark, perfMeasure } from "@/services/perf";
import type { ExplorerOpenPayload } from "@/store/explorer-drawer-store";
import { useExplorerDrawerStore } from "@/store/explorer-drawer-store";

/** Open drawer immediately; resolve route in background if needed. */
export function openExplorerFromContext(
  openDrawer: (target: ExplorerOpenPayload) => void,
  contextKey: string,
  title?: string
) {
  perfMark("explorer-drawer-open");
  const hint = resolveContextTarget(contextKey, title);
  openDrawer({
    entityType: hint.entityType,
    entityId: hint.entityId,
    title: hint.title ?? title,
    contextKey,
  });
  void fetchExplorerContextRoute(contextKey).then((res) => {
    if (!res.success || !res.data) return;
    const d = res.data;
    const current = useExplorerDrawerStore.getState().target;
    if (!current || current.contextKey !== contextKey) return;
    if (current.entityType === d.entity_type && current.entityId === d.entity_id) {
      perfMeasure("explorer-context-route", "explorer-drawer-open");
      return;
    }
    openDrawer({
      entityType: d.entity_type,
      entityId: d.entity_id,
      title: title ?? d.title,
      contextKey,
    });
    perfMeasure("explorer-context-route", "explorer-drawer-open");
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
    perfMark("explorer-drawer-open");
    openDrawer({ ...target.explorer, title: target.title });
    return;
  }
  if (target.context) {
    openExplorerFromContext(openDrawer, target.context, target.title);
  }
}
