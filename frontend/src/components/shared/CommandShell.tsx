"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { useAuth } from "@/hooks/useAuth";

const NAV = [
  { href: "/regulator", label: "Overview" },
  { href: "/command-center", label: "Command" },
  { href: "/command-center/threat-map", label: "Threat Map" },
  { href: "/command-center/incidents", label: "Incidents" },
  { href: "/command-center/approvals", label: "Approvals" },
  { href: "/emergency-ops", label: "Emergency" },
  { href: "/regulator/analytics", label: "Analytics" },
];

export function CommandShell({ children, title }: { children: React.ReactNode; title: string }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-sovereign-950 text-slate-100">
      <aside className="flex w-64 flex-col border-r border-sovereign-800 bg-sovereign-900/90">
        <div className="border-b border-sovereign-800 px-5 py-6">
          <p className="text-xs uppercase tracking-widest text-sovereign-accent">NPTTE PharmaNG</p>
          <h1 className="mt-1 text-lg font-semibold">National Command</h1>
        </div>
        <nav className="flex-1 space-y-1 p-3">
          {NAV.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "block rounded-lg px-3 py-2 text-sm transition",
                pathname === item.href || pathname.startsWith(item.href + "/")
                  ? "bg-sovereign-accent/20 text-sovereign-accent"
                  : "text-slate-400 hover:bg-sovereign-800 hover:text-white"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="border-t border-sovereign-800 p-4 text-xs text-slate-500">
          <p className="truncate font-medium text-slate-300">{user?.username}</p>
          <p className="truncate">{user?.role_code}</p>
          <button
            type="button"
            onClick={logout}
            className="mt-3 w-full rounded border border-sovereign-700 py-1.5 text-slate-300 hover:bg-sovereign-800"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex flex-1 flex-col">
        <header className="flex items-center justify-between border-b border-sovereign-800 bg-sovereign-900/50 px-8 py-4 backdrop-blur">
          <h2 className="text-xl font-semibold tracking-tight">{title}</h2>
          <span className="rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400">
            LIVE · Sovereign Infrastructure
          </span>
        </header>
        <div className="flex-1 overflow-auto p-8">{children}</div>
      </main>
    </div>
  );
}
