"use client";

import { useParams } from "next/navigation";
import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { RegionalCommandPanel } from "@/components/regional/RegionalCommandPanel";

const LABELS: Record<string, string> = {
  south_west: "South West",
  south_east: "South East",
  south_south: "South South",
  north_central: "North Central",
  north_east: "North East",
  north_west: "North West",
};

export default function RegionalDetailPage() {
  const params = useParams<{ regionKey: string }>();
  const key = params.regionKey ?? "south_west";
  const label = LABELS[key] ?? key;

  return (
    <RegulatorGuard>
      <CommandShell title={`Regional · ${label}`}>
        <RegionalCommandPanel regionKey={key} label={label} />
      </CommandShell>
    </RegulatorGuard>
  );
}
