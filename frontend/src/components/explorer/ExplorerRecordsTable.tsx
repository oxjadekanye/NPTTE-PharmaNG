export function ExplorerRecordsTable({
  records,
  filter,
  onFilterChange,
}: {
  records: Record<string, unknown>[];
  filter: string;
  onFilterChange: (v: string) => void;
}) {
  return (
    <section>
      <div className="flex items-center justify-between gap-2">
        <h4 className="text-[11px] font-semibold uppercase text-slate-400">Operational records</h4>
        <input
          type="search"
          placeholder="Filter…"
          value={filter}
          onChange={(ev) => onFilterChange(ev.target.value)}
          className="w-28 rounded border border-sovereign-700 bg-sovereign-900 px-2 py-0.5 text-[10px] text-white"
        />
      </div>
      <div className="mt-2 max-h-52 overflow-auto rounded border border-sovereign-800">
        <table className="w-full text-left text-[11px]">
          <thead className="sticky top-0 bg-sovereign-900 text-slate-500">
            <tr>
              <th className="px-2 py-1">Record</th>
              <th className="px-2 py-1">Status</th>
            </tr>
          </thead>
          <tbody>
            {records.length === 0 && (
              <tr>
                <td colSpan={2} className="px-2 py-3 text-slate-500">
                  No records
                </td>
              </tr>
            )}
            {records.slice(0, 50).map((row, i) => (
              <tr key={String(row.id ?? i)} className="border-t border-sovereign-800/60 hover:bg-sovereign-800/30">
                <td className="px-2 py-1 text-slate-200">
                  {String(row.title ?? row.name ?? row.cluster_code ?? row.case_reference ?? row.id ?? i)}
                </td>
                <td className="px-2 py-1 text-slate-500">
                  {String(row.status ?? row.severity ?? row.case_status ?? "—")}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </section>
  );
}
