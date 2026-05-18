"use client";

import { useState } from "react";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { PILOT_GUIDES } from "@/content/pilot-docs";

export default function DocumentationCenterPage() {
  const [active, setActive] = useState(PILOT_GUIDES[0]);

  return (
    <RegulatorGuard>
      <CommandShell title="Documentation Center">
        <div className="flex flex-col gap-6 lg:flex-row">
          <ul className="lg:w-56 space-y-1">
            {PILOT_GUIDES.map((g) => (
              <li key={g.id}>
                <button
                  type="button"
                  onClick={() => setActive(g)}
                  className={`w-full rounded-lg px-3 py-2 text-left text-sm ${
                    active.id === g.id ? "bg-sovereign-accent/20 text-sovereign-accent" : "text-slate-400"
                  }`}
                >
                  {g.title}
                </button>
              </li>
            ))}
          </ul>
          <article className="glass-panel flex-1 rounded-xl border border-sovereign-800 p-6">
            <h3 className="text-lg font-semibold text-white">{active.title}</h3>
            {active.sections.map((s) => (
              <section key={s.heading} className="mt-4">
                <h4 className="text-sm font-medium text-sovereign-accent">{s.heading}</h4>
                <p className="mt-1 text-sm text-slate-400">{s.body}</p>
              </section>
            ))}
          </article>
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
