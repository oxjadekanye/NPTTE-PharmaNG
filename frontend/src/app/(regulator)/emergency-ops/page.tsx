"use client";

import { CommandShell } from "@/components/shared/CommandShell";
import { RegulatorGuard } from "@/components/shared/RegulatorGuard";
import { API_BASE } from "@/services/api-client";

export default function EmergencyOpsPage() {
  async function activate() {
    const token = localStorage.getItem("nptte_access_token");
    await fetch(`${API_BASE}/emergency-response/activate/`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
        Authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        protocol_code: "NATIONAL-CRISIS",
        title: "Emergency distribution activated from command UI",
        target_states: ["Lagos", "FCT"],
      }),
    });
    alert("Emergency protocol activation requested");
  }

  return (
    <RegulatorGuard>
      <CommandShell title="Emergency Operations">
        <p className="mb-6 text-sm text-slate-400">
          Shortage monitoring · strategic reserves · crisis redistribution mode
        </p>
        <button
          type="button"
          onClick={activate}
          className="rounded-lg bg-red-600 px-6 py-3 text-sm font-semibold text-white hover:bg-red-500"
        >
          Activate emergency distribution mode
        </button>
      </CommandShell>
    </RegulatorGuard>
  );
}
