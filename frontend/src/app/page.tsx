import Link from "next/link";

export default function HomePage() {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-sovereign-950 px-6 text-center">
      <p className="text-sm uppercase tracking-[0.3em] text-sovereign-accent">Federal Republic of Nigeria</p>
      <h1 className="mt-4 max-w-2xl text-4xl font-semibold text-white md:text-5xl">
        National Pharmaceutical Transparency &amp; Traceability Ecosystem
      </h1>
      <p className="mt-4 max-w-xl text-slate-400">
        Sovereign infrastructure for medicine verification, regulator command operations, and
        national supply chain intelligence.
      </p>
      <div className="mt-10 flex flex-wrap justify-center gap-4">
        <Link
          href="/login"
          className="rounded-lg bg-sovereign-accent px-6 py-3 text-sm font-medium text-sovereign-950"
        >
          Regulator sign in
        </Link>
        <Link
          href="/citizen"
          className="rounded-lg border border-sovereign-700 px-6 py-3 text-sm text-slate-200 hover:bg-sovereign-900"
        >
          Verify medicine
        </Link>
      </div>
    </div>
  );
}
