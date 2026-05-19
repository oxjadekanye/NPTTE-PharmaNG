"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import clsx from "clsx";
import { useAuth } from "@/hooks/useAuth";
import { CommandModeToggle } from "@/components/command/CommandModeToggle";
import { DemoBadge } from "@/components/command/DemoBadge";
import { IntelligenceDetailDrawer } from "@/components/explorer/IntelligenceDetailDrawer";
import { COMMAND_NAV_SECTIONS } from "@/config/navigation";

export function CommandShell({ children, title }: { children: React.ReactNode; title: string }) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-sovereign-950 text-slate-100">
      <aside className="flex w-64 shrink-0 flex-col border-r border-sovereign-800 bg-sovereign-900/95 shadow-xl">
        <div className="border-b border-sovereign-800 px-5 py-6">
          <p className="text-xs uppercase tracking-widest text-sovereign-accent">NPTTE PharmaNG</p>
          <h1 className="mt-1 text-lg font-semibold leading-tight">National Command</h1>
          <div className="mt-3">
            <DemoBadge />
          </div>
        </div>
        <nav className="flex-1 space-y-4 overflow-y-auto p-3">
          {COMMAND_NAV_SECTIONS.map((section) => (
            <div key={section.title}>
              <p className="mb-1 px-3 text-[10px] font-semibold uppercase tracking-widest text-slate-600">
                {section.title}
              </p>
              <div className="space-y-0.5">
                {section.items.map((item) => (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={clsx(
                      "block rounded-lg px-3 py-2 text-sm font-medium transition duration-200",
                      pathname === item.href ||
                        (item.href !== "/regulator" &&
                          item.href !== "/regulator/explorer" &&
                          pathname.startsWith(item.href + "/")) ||
                        (item.href === "/regulator/explorer" && pathname.startsWith("/regulator/explorer"))
                        ? "bg-sovereign-accent/20 text-sovereign-accent shadow-inner"
                        : "text-slate-400 hover:bg-sovereign-800 hover:text-white"
                    )}
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            </div>
          ))}
        </nav>
        <div className="border-t border-sovereign-800 p-4 text-xs text-slate-500">
          <p className="truncate font-medium text-slate-300">{user?.username}</p>
          <p className="truncate">{user?.role_code}</p>
          <button
            type="button"
            onClick={logout}
            className="mt-3 w-full rounded-lg border border-sovereign-700 py-2 text-slate-300 transition hover:bg-sovereign-800 hover:text-white"
          >
            Sign out
          </button>
        </div>
      </aside>
      <main className="flex min-w-0 flex-1 flex-col">
        <header className="flex flex-wrap items-center justify-between gap-4 border-b border-sovereign-800 bg-sovereign-900/60 px-6 py-4 backdrop-blur-md lg:px-8">
          <h2 className="text-xl font-semibold tracking-tight text-white">{title}</h2>
          <div className="flex flex-wrap items-center gap-3">
            <CommandModeToggle />
            <span className="hidden items-center gap-2 rounded-full bg-emerald-500/10 px-3 py-1 text-xs text-emerald-400 sm:inline-flex">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              LIVE · Sovereign Infrastructure
            </span>
          </div>
        </header>
        <div className="flex-1 overflow-auto p-6 lg:p-8">{children}</div>
        <IntelligenceDetailDrawer />
      </main>
    </div>
  );
}
