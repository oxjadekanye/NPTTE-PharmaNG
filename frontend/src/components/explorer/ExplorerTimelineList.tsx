export function ExplorerTimelineList({ items }: { items: Record<string, unknown>[] }) {
  if (!items.length) {
    return <p className="text-xs text-slate-500">No timeline entries.</p>;
  }
  return (
    <ul className="max-h-48 space-y-2 overflow-y-auto">
      {items.map((e, i) => (
        <li key={String(e.id ?? i)} className="border-l-2 border-sovereign-accent/50 pl-3 text-xs">
          <p className="font-medium text-slate-200">{String(e.summary ?? e.title ?? e.entry_type)}</p>
          <p className="text-[10px] text-slate-500">
            {String(e.entry_type ?? "")}
            {e.created_at ? ` · ${new Date(String(e.created_at)).toLocaleString()}` : ""}
          </p>
        </li>
      ))}
    </ul>
  );
}
