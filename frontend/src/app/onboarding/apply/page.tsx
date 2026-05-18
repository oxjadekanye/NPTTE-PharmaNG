"use client";

import { FormEvent, useState } from "react";
import Link from "next/link";
import { applyOrganisationOnboarding } from "@/services/tenancy";

export default function OnboardingApplyPage() {
  const [form, setForm] = useState({
    organisation_type: "pharmacy",
    legal_name: "",
    trading_name: "",
    registration_number: "",
    license_number: "",
    cac_number: "",
    state: "",
    city: "",
    contact_email: "",
  });
  const [result, setResult] = useState<Record<string, string> | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError(null);
    try {
      const res = await applyOrganisationOnboarding(form);
      setResult(res.data as Record<string, string>);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Application failed");
    }
  }

  return (
    <div className="min-h-screen bg-sovereign-950 px-4 py-10 text-slate-100">
      <h1 className="text-2xl font-semibold">Organisation onboarding</h1>
      <p className="mt-2 max-w-lg text-sm text-slate-500">
        Apply for NPTTE national registry access. Regulator review required before activation.
      </p>
      <form onSubmit={onSubmit} className="mx-auto mt-8 max-w-lg space-y-3">
        <select
          value={form.organisation_type}
          onChange={(e) => setForm({ ...form, organisation_type: e.target.value })}
          className="w-full rounded border border-sovereign-700 bg-sovereign-900 px-3 py-2 text-sm"
        >
          <option value="manufacturer">Manufacturer</option>
          <option value="pharmacy">Pharmacy</option>
          <option value="distributor">Distributor</option>
          <option value="warehouse">Warehouse</option>
          <option value="hospital">Hospital</option>
          <option value="customs">Customs</option>
        </select>
        {(["legal_name", "trading_name", "registration_number", "license_number", "cac_number", "state", "city", "contact_email"] as const).map((field) => (
          <input
            key={field}
            placeholder={field.replace(/_/g, " ")}
            value={form[field]}
            onChange={(e) => setForm({ ...form, [field]: e.target.value })}
            className="w-full rounded border border-sovereign-700 bg-sovereign-900 px-3 py-2 text-sm"
          />
        ))}
        <button type="submit" className="w-full rounded-lg bg-sovereign-accent py-3 font-semibold text-sovereign-950">
          Submit application
        </button>
      </form>
      {error && <p className="mt-4 text-sm text-rose-300">{error}</p>}
      {result && (
        <p className="mt-4 text-sm text-emerald-300">
          Application created — organisation {result.organisation_id} (status: {result.status})
        </p>
      )}
      <Link href="/login" className="mt-6 inline-block text-sm text-sovereign-accent hover:underline">
        Operator login
      </Link>
    </div>
  );
}
