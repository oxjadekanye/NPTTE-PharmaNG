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

  if (loading) {
    return (
      <div className="flex min-h-screen items-center justify-center bg-sovereign-950 text-slate-400">
        Initializing sovereign command session…
      </div>
    );
  }

  if (!isAuthenticated) return null;
  return <>{children}</>;
}
