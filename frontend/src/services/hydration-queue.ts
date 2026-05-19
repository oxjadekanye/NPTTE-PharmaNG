/** Prioritized background hydration with concurrency limits. */
type Task = {
  id: string;
  priority: number;
  run: (signal: AbortSignal) => Promise<void>;
};

const MAX_CONCURRENT = 3;
let active = 0;
const queue: Task[] = [];
const inflight = new Map<string, AbortController>();

function sortQueue() {
  queue.sort((a, b) => b.priority - a.priority);
}

function pump() {
  while (active < MAX_CONCURRENT && queue.length > 0) {
    const task = queue.shift();
    if (!task) break;
    if (inflight.has(task.id)) continue;
    const ac = new AbortController();
    inflight.set(task.id, ac);
    active += 1;
    void task
      .run(ac.signal)
      .catch(() => {
        /* swallowed — widgets handle own errors */
      })
      .finally(() => {
        active -= 1;
        inflight.delete(task.id);
        pump();
      });
  }
}

/** Enqueue hydration work. Higher priority runs first. Replaces same id. */
export function enqueueHydration(
  id: string,
  run: (signal: AbortSignal) => Promise<void>,
  priority = 0
): void {
  cancelHydration(id);
  queue.push({ id, priority, run });
  sortQueue();
  pump();
}

export function cancelHydration(id: string): void {
  const ac = inflight.get(id);
  if (ac) {
    ac.abort();
    inflight.delete(id);
  }
  const idx = queue.findIndex((t) => t.id === id);
  if (idx >= 0) queue.splice(idx, 1);
}

export function cancelAllHydration(): void {
  for (const ac of inflight.values()) ac.abort();
  inflight.clear();
  queue.length = 0;
}

export const HydrationPriority = {
  SHELL: 100,
  ROUTE: 80,
  WIDGET: 50,
  HOVER: 30,
  PREFETCH: 10,
  BACKGROUND: 5,
} as const;
