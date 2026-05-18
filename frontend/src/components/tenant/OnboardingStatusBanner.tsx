"use client";

export function OnboardingStatusBanner({ status }: { status?: string }) {
  if (!status || status === "approved" || status === "active") return null;
  const tone =
    status === "rejected"
      ? "border-rose-500/50 bg-rose-500/10 text-rose-100"
      : "border-amber-500/50 bg-amber-500/10 text-amber-100";
  return (
    <div className={`mb-4 rounded-lg border px-4 py-2 text-sm ${tone}`}>
      Organisation onboarding status: <strong>{status.replace(/_/g, " ")}</strong>
    </div>
  );
}
