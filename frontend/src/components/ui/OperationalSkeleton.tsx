"use client";

export function OperationalSkeleton({ rows = 4 }: { rows?: number }) {
  return (
    <div className="animate-pulse space-y-3" aria-hidden>
      {Array.from({ length: rows }).map((_, i) => (
        <div
          key={i}
          className="h-14 rounded-lg border border-sovereign-800 bg-sovereign-900/60"
        />
      ))}
    </div>
  );
}
