type GraphNode = { id: string; label: string; kind?: string };
type GraphEdge = { source: string; target: string; relation?: string };

export function ExplorerRelatedCards({ related }: { related: Record<string, unknown> | null }) {
  const nodes = (related?.nodes as GraphNode[]) ?? [];
  const edges = (related?.edges as GraphEdge[]) ?? [];
  if (!nodes.length) return <p className="text-xs text-slate-500">No related entities mapped.</p>;
  return (
    <div className="space-y-2">
      <div className="grid gap-2 sm:grid-cols-2">
        {nodes.map((n) => (
          <div key={n.id} className="rounded border border-sovereign-700/60 bg-sovereign-900/40 px-2 py-2 text-xs">
            <p className="font-medium text-slate-200">{n.label}</p>
            <p className="text-[10px] text-slate-500">{n.kind ?? n.id}</p>
          </div>
        ))}
      </div>
      {edges.length > 0 && (
        <p className="text-[10px] text-slate-500">{edges.length} relationship edge(s) in graph</p>
      )}
    </div>
  );
}
