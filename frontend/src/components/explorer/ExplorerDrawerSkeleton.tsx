export function ExplorerDrawerSkeleton() {
  return (
    <div className="animate-pulse space-y-4 p-1">
      <div className="h-4 w-2/3 rounded bg-sovereign-800" />
      <div className="h-3 w-1/2 rounded bg-sovereign-800/80" />
      <div className="h-20 rounded-lg bg-sovereign-900/80" />
      <div className="h-16 rounded-lg bg-sovereign-900/60" />
      <div className="h-16 rounded-lg bg-sovereign-900/60" />
      <div className="h-24 rounded-lg bg-sovereign-900/60" />
    </div>
  );
}
