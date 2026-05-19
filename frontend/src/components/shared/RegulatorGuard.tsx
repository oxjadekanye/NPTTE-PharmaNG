"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { hasPermission } from "@/store/auth-store";

export function RegulatorGuard({
  children,
  permission = "regulatory.read",
}: {
  children: React.ReactNode;
  permission?: string;
}) {
  const { isAuthenticated, loading, permissions } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !isAuthenticated) router.replace("/login");
    if (!loading && isAuthenticated && !hasPermission(permissions, permission)) {
      router.replace("/login?error=unauthorized");
    }
  }, [loading, isAuthenticated, permissions, permission, router]);

  if (loading && !isAuthenticated) {
    return (
      <div className="flex min-h-screen items-center justify-center gap-2 bg-sovereign-950 text-sm text-slate-400">
        <span className="h-2 w-2 animate-pulse rounded-full bg-sovereign-accent" />
        Loading…
      </div>
    );
  }

  if (!isAuthenticated) return null;
  return <>{children}</>;
}
