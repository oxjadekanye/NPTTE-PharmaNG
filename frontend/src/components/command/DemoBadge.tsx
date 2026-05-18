import { DEMO_LABEL } from "@/demo/nigeria-intelligence";

export function DemoBadge() {
  return (
    <span
      className="rounded border border-slate-600/60 bg-slate-800/80 px-2 py-0.5 text-[10px] font-medium uppercase tracking-wider text-slate-400"
      title="Simulated intelligence for demonstration"
    >
      {DEMO_LABEL}
    </span>
  );
}
