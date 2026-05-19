"use client";

import Link from "next/link";
import { useParams } from "next/navigation";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { OperationalMap } from "@/components/maps/OperationalMap";

export default function LayerMapPage() {
  const params = useParams<{ layer: string }>();
  const layer = params.layer ?? "operational";

  return (
    <RegulatorGuard>
      <CommandShell title={`Map · ${layer}`}>
        <Link href="/regulator/map" className="text-xs text-sovereign-accent hover:underline">
          ← National map hub
        </Link>
        <div className="mt-4">
          <OperationalMap layer={layer} />
        </div>
      </CommandShell>
    </RegulatorGuard>
  );
}
