"use client";

import Link from "next/link";

const STORY = [
  {
    title: "The national problem",
    body: "Counterfeit medicines, fragmented supply chains, and limited visibility cost Nigerian lives and billions in economic harm.",
  },
  {
    title: "The NPTTE solution",
    body: "A sovereign national pharmaceutical traceability and intelligence platform — from manufacturer to citizen scan.",
  },
  {
    title: "National Command Center",
    body: "Regulators orchestrate threats, incidents, recalls, and executive intelligence in real time.",
    href: "/command-center",
  },
  {
    title: "Traceability engine",
    body: "Immutable batch registry, serialization, custody ledger, and regulatory approval workflows.",
    href: "/regulator/traceability",
  },
  {
    title: "Citizen verification",
    body: "Every Nigerian can verify medicine authenticity with a scan — building national trust.",
    href: "/citizen",
  },
  {
    title: "Ecosystem portals",
    body: "Manufacturers, pharmacies, warehouses, customs, hospitals — one connected national operating system.",
    href: "/manufacturer",
  },
  {
    title: "National impact",
    body: "Reduced counterfeit penetration, faster recalls, data-driven regulation, and investor-grade infrastructure.",
  },
  {
    title: "Roadmap",
    body: "Pilot launch → regional scale → GS1 interoperability → full government systems integration.",
  },
];

export default function PilotPresentationPage() {
  return (
    <div className="min-h-screen bg-gradient-to-b from-sovereign-950 via-[#0a1628] to-sovereign-950 text-slate-100">
      <header className="sticky top-0 z-20 border-b border-sovereign-800/80 bg-sovereign-950/90 backdrop-blur-md">
        <div className="mx-auto flex max-w-5xl items-center justify-between px-6 py-4">
          <div>
            <p className="text-[10px] uppercase tracking-[0.3em] text-sovereign-accent">NPTTE PharmaNG</p>
            <h1 className="text-xl font-semibold">Pilot Presentation Mode</h1>
          </div>
          <div className="flex gap-3 text-sm">
            <Link href="/login" className="text-sovereign-accent hover:underline">
              Regulator login
            </Link>
            <Link href="/citizen" className="text-slate-400 hover:text-white">
              Citizen verify
            </Link>
          </div>
        </div>
      </header>

      <section className="mx-auto max-w-5xl px-6 py-20 text-center">
        <p className="text-sm uppercase tracking-widest text-sovereign-accent">Sovereign pharmaceutical infrastructure</p>
        <h2 className="mt-4 text-4xl font-semibold leading-tight md:text-5xl">
          Nigeria&apos;s national medicine
          <br />
          <span className="text-sovereign-accent">integrity platform</span>
        </h2>
        <p className="mx-auto mt-6 max-w-2xl text-lg text-slate-400">
          Built for regulators, industry, pharmacies, and citizens — production-deployed and pilot-ready.
        </p>
        <Link
          href="/regulator/pilot-readiness"
          className="neon-alert mt-10 inline-block rounded-full bg-sovereign-accent px-8 py-3 text-sm font-medium text-sovereign-950"
        >
          Open pilot readiness dashboard
        </Link>
      </section>

      <section className="mx-auto max-w-5xl space-y-8 px-6 pb-24">
        {STORY.map((slide, i) => (
          <article
            key={slide.title}
            className="glass-panel operational-glow scroll-mt-24 rounded-2xl border border-sovereign-800/80 p-8 transition hover:border-sovereign-accent/40"
            style={{ animationDelay: `${i * 80}ms` }}
          >
            <p className="text-[10px] font-mono text-sovereign-accent">0{i + 1}</p>
            <h3 className="mt-2 text-2xl font-semibold text-white">{slide.title}</h3>
            <p className="mt-3 text-slate-400 leading-relaxed">{slide.body}</p>
            {"href" in slide && slide.href && (
              <Link href={slide.href} className="mt-4 inline-block text-sm text-sovereign-accent hover:underline">
                Explore live module →
              </Link>
            )}
          </article>
        ))}
      </section>

      <footer className="border-t border-sovereign-800 py-8 text-center text-xs text-slate-600">
        DEMO/SIMULATED intelligence overlays remain available for stakeholder demonstrations.
      </footer>
    </div>
  );
}
