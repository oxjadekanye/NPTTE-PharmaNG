import type { ReactNode } from "react";
import Link from "next/link";
import clsx from "clsx";
import { usePathname } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { DemoBadge } from "@/components/command/DemoBadge";
import { NotificationCenter } from "@/components/notifications/NotificationCenter";
import { OperationalBanners } from "@/components/operations/OperationalBanners";
import { OrganisationSwitcher } from "@/components/tenant/OrganisationSwitcher";
import type { PortalNavItem } from "@/config/portal-nav";

export function EnterprisePortalShell({
  title,
  subtitle,
  nav,
  children,
  badge = "Phase 9 · National Ecosystem",
}: {
  title: string;
  subtitle?: string;
  nav: PortalNavItem[];
  children: ReactNode;
  badge?: string;
}) {
  const pathname = usePathname();
  const { user, logout } = useAuth();

  return (
    <div className="flex min-h-screen bg-sovereign-950 text-slate-100">
      <aside className="flex w-64 shrink-0 flex-col border-r border-sovereign-800 bg-sovereign-900/95 shadow-xl">
        <div className="border-b border-sovereign-800 px-5 py-6">
          <p className="text-[10px] uppercase tracking-widest text-sovereign-accent">{badge}</p>
          <h1 className="mt-1 text-lg font-semibold leading-tight">{title}</h1>
          {subtitle && <p className="mt-1 text-xs text-slate-500">{subtitle}</p>}
          <div className="mt-3">
            <DemoBadge />
          </div>
        </div>
        <nav className="flex-1 space-y-0.5 overflow-y-auto p-3">
          {nav.map((item) => (
            <Link
              key={item.href}
              href={item.href}
              className={clsx(
                "block rounded-lg px-3 py-2.5 text-sm font-medium transition duration-200",
                pathname === item.href || pathname.startsWith(item.href + "/")
                  ? "bg-sovereign-accent/20 text-sovereign-accent shadow-inner"
                  : "text-slate-400 hover:bg-sovereign-800 hover:text-white"
              )}
            >
              {item.label}
            </Link>
          ))}
        </nav>
        <div className="border-t border-sovereign-800 p-4 text-xs text-slate-500">
          <Link href="/regulator" className="mb-2 block text-sovereign-accent hover:underline">
            ← National Command
          </Link>
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
          <div>
            <h2 className="text-xl font-semibold tracking-tight text-white">{title}</h2>
            {subtitle && <p className="text-xs text-slate-500">{subtitle}</p>}
          </div>
          <div className="flex flex-wrap items-center gap-3">
            <NotificationCenter compact />
            <OrganisationSwitcher />
            <span className="inline-flex items-center gap-2 rounded-full border border-emerald-500/30 bg-emerald-500/10 px-3 py-1 text-xs text-emerald-300">
              <span className="h-1.5 w-1.5 animate-pulse rounded-full bg-emerald-400" />
              Tenant-scoped · Simulated feed
            </span>
          </div>
        </header>
        <OperationalBanners />
        <div className="flex-1 overflow-auto p-6 lg:p-8">{children}</div>
      </main>
    </div>
  );
}
