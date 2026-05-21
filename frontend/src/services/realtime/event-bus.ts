/** Phase 11 — lightweight in-process event bus (polling transport). */

export type OperationalEventKind =
  | "scan"
  | "recall_alert"
  | "pharmacy_incident"
  | "inventory"
  | "regulator_broadcast"
  | "enforcement"
  | "task";

type Listener = (payload: unknown) => void;

const listeners = new Map<string, Set<Listener>>();

export function subscribeOperational(kind: OperationalEventKind | "*", fn: Listener) {
  const key = kind;
  if (!listeners.has(key)) listeners.set(key, new Set());
  listeners.get(key)!.add(fn);
  return () => listeners.get(key)?.delete(fn);
}

export function publishOperational(kind: OperationalEventKind, payload: unknown) {
  listeners.get(kind)?.forEach((fn) => fn(payload));
  listeners.get("*")?.forEach((fn) => fn({ kind, payload }));
}

export function clearOperationalBus() {
  listeners.clear();
}
