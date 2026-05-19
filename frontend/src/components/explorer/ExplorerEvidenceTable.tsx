export function ExplorerEvidenceTable({ items }: { items: Record<string, unknown>[] }) {
  if (!items.length) return <p className="text-xs text-slate-500">No evidence artifacts.</p>;
  return (
    <div className="max-h-40 overflow-auto rounded border border-sovereign-800">
      <table className="w-full text-left text-[11px]">
        <thead className="bg-sovereign-900 text-slate-500">
          <tr>
            <th className="px-2 py-1">Kind</th>
            <th className="px-2 py-1">Detail</th>
          </tr>
        </thead>
        <tbody>
          {items.map((row, i) => (
            <tr key={i} className="border-t border-sovereign-800/80">
              <td className="px-2 py-1 text-slate-400">{String(row.kind ?? "evidence")}</td>
              <td className="px-2 py-1 text-slate-300">
                {typeof row.payload === "object"
                  ? JSON.stringify(row.payload).slice(0, 120)
                  : String(row.payload ?? row.summary ?? "—")}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
