"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { hasPermission } from "@/store/auth-store";

const ENTERPRISE_PERMISSIONS = [
  "supply_chain.read",
  "pharmacy.profile",
  "pharmacy.profile.read",
  "logistics.read",
  "hospital.profile",
  "hospital.read",
  "customs.read",
  "organisation.read",
  "organisation.admin",
  "regulatory.read",
  "admin.all",
];

export function EnterpriseGuard({ children }: { children: React.ReactNode }) {
  const { isAuthenticated, loading, permissions } = useAuth();
  const router = useRouter();
  const allowed = ENTERPRISE_PERMISSIONS.some((p) => hasPermission(permissions, p));

  useEffect(() => {
    if (!loading && !isAuthenticated) router.replace("/login");
    if (!loading && isAuthenticated && !allowed) router.replace("/login?error=unauthorized");
  }, [loading, isAuthenticated, allowed, router]);

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-sovereign-950 text-slate-400">
        Loading organisation workspace…
      </div>
    );
  }
  if (!isAuthenticated || !allowed) return null;
  return <>{children}</>;
}
