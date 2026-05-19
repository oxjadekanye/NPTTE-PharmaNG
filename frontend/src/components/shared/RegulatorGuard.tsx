"use client";

import { useEffect, useState } from "react";
import { useRouter } from "next/navigation";
import { useAuth } from "@/hooks/useAuth";
import { hasPermission } from "@/store/auth-store";
import { applyShellFromCache } from "@/services/auth-shell-bootstrap";

export function RegulatorGuard({
  children,
  permission = "regulatory.read",
}: {
  children: React.ReactNode;
  permission?: string;
}) {
  const { isAuthenticated, permissions } = useAuth();
  const router = useRouter();
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const token = typeof window !== "undefined" ? localStorage.getItem("nptte_access_token") : null;
    if (!token) {
      router.replace("/login");
      return;
    }
    applyShellFromCache();
    setReady(true);
  }, [router]);

  useEffect(() => {
    if (!ready) return;
    if (!isAuthenticated) {
      const token = localStorage.getItem("nptte_access_token");
      if (!token) router.replace("/login");
      return;
    }
    if (!hasPermission(permissions, permission)) {
      router.replace("/login?error=unauthorized");
    }
  }, [ready, isAuthenticated, permissions, permission, router]);

  if (!ready) {
    return (
      <div className="flex min-h-screen bg-sovereign-950">
        <aside className="w-64 shrink-0 border-r border-sovereign-800 bg-sovereign-900/95" />
        <main className="flex flex-1 flex-col">
          <header className="h-16 border-b border-sovereign-800 bg-sovereign-900/60" />
          <div className="flex-1 animate-pulse bg-sovereign-900/30 p-6" aria-hidden="true" />
        </main>
      </div>
    );
  }

  return <>{children}</>;
}
