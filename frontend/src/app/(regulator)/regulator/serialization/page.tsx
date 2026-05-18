"use client";

import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { SerializationDashboard } from "@/components/serialization/SerializationDashboard";

export default function SerializationOperationsPage() {
  return (
    <RegulatorGuard>
      <CommandShell title="National Serialization Operations">
        <SerializationDashboard />
      </CommandShell>
    </RegulatorGuard>
  );
}
