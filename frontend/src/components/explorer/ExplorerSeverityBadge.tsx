import clsx from "clsx";

export function ExplorerSeverityBadge({ severity }: { severity?: string }) {
  const s = (severity ?? "info").toLowerCase();
  const styles =
    s === "critical" || s === "red"
      ? "bg-red-500/20 text-red-200 border-red-500/40"
      : s === "high" || s === "warning" || s === "amber"
        ? "bg-amber-500/20 text-amber-200 border-amber-500/40"
        : s === "medium"
          ? "bg-orange-500/15 text-orange-200 border-orange-500/30"
          : "bg-emerald-500/15 text-emerald-200 border-emerald-500/30";
  return (
    <span className={clsx("inline-flex rounded-full border px-2 py-0.5 text-[10px] font-semibold uppercase", styles)}>
      {severity ?? "info"}
    </span>
  );
}
