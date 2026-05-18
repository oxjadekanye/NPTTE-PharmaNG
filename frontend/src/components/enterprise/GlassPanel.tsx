"use client";

import type { ReactNode } from "react";
import clsx from "clsx";

export function GlassPanel({
  title,
  subtitle,
  children,
  className,
  accent = "sky",
}: {
  title: string;
  subtitle?: string;
  children: ReactNode;
  className?: string;
  accent?: "emerald" | "sky" | "amber" | "rose";
}) {
  const glow =
    accent === "emerald"
      ? "from-emerald-500/10"
      : accent === "amber"
        ? "from-amber-500/10"
        : accent === "rose"
          ? "from-rose-500/10"
          : "from-sky-500/10";
  return (
    <section
      className={clsx(
        "glass-panel relative overflow-hidden rounded-xl border border-sovereign-800/90 p-5 shadow-lg",
        className
      )}
    >
      <div className={clsx("pointer-events-none absolute inset-0 bg-gradient-to-br to-transparent opacity-40", glow)} />
      <div className="relative">
        <h3 className="text-sm font-semibold text-white">{title}</h3>
        {subtitle && <p className="mt-0.5 text-xs text-slate-500">{subtitle}</p>}
        <div className="mt-4">{children}</div>
      </div>
    </section>
  );
}
