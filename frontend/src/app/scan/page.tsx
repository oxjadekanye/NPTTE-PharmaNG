"use client";

import Link from "next/link";

const MODES = [
  { href: "/citizen/scan", label: "Citizen verify", desc: "Authenticity check" },
  { href: "/pharmacy/scan", label: "Pharmacy", desc: "Receive & dispense" },
  { href: "/regulator/field-inspection", label: "Regulator inspection", desc: "Field checklist" },
  { href: "/customs/scan", label: "Customs", desc: "Import verification" },
  { href: "/warehouse/scan", label: "Warehouse", desc: "Receiving & cold chain" },
];

export default function ScanHubPage() {
  return (
    <div className="min-h-screen bg-sovereign-950 px-4 py-8 text-slate-100 sm:px-6">
      <h1 className="text-2xl font-semibold">Mobile scan operations</h1>
      <p className="mt-2 max-w-md text-sm text-slate-500">
        National traceability scanning — camera QR, barcode, or manual serial entry with offline
        queue sync.
      </p>
      <ul className="mx-auto mt-8 grid max-w-lg gap-3">
        {MODES.map((m) => (
          <li key={m.href}>
            <Link
              href={m.href}
              className="block rounded-xl border border-sovereign-800 bg-sovereign-900/60 px-4 py-4 transition hover:border-sovereign-accent/50"
            >
              <span className="font-medium text-sovereign-accent">{m.label}</span>
              <span className="mt-1 block text-xs text-slate-500">{m.desc}</span>
            </Link>
          </li>
        ))}
      </ul>
      <Link href="/citizen" className="mt-8 inline-block text-xs text-slate-500 hover:text-slate-300">
        Citizen portal
      </Link>
    </div>
  );
}
