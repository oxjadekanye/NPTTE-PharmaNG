"use client";

import Link from "next/link";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalMap } from "@/components/maps/OperationalMap";

const LAYERS = [
  { href: "/regulator/map/counterfeit", label: "Counterfeit hotspots" },
  { href: "/regulator/map/recalls", label: "Recall impact" },
  { href: "/regulator/map/investigations", label: "Investigations" },
  { href: "/regulator/map/shortage", label: "Shortage pressure" },
  { href: "/regulator/map/enforcement", label: "Enforcement deployment" },
  { href: "/regulator/map/customs", label: "Customs / border" },
];

export default function NationalMapPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="National operational map">
        <div className="mb-4 flex flex-wrap gap-2 text-xs">
          {LAYERS.map((l) => (
            <Link key={l.href} href={l.href} className="rounded border border-sovereign-700 px-2 py-1 text-sovereign-accent">
              {l.label}
            </Link>
          ))}
          <Link href="/command-room" className="rounded border border-sovereign-accent/50 px-2 py-1 text-sovereign-accent">
            Command room →
          </Link>
        </div>
        <OperationalMap layer="operational" />
      </CommandShell>
    </RegulatorGuard>
  );
}
