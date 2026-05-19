"use client";

import { memo } from "react";

export const ExplorerOrganisationCard = memo(function ExplorerOrganisationCard({
  name,
  state,
  phone,
  address,
}: {
  name?: string;
  state?: string;
  phone?: string;
  address?: string;
}) {
  return (
    <div className="rounded border border-sovereign-800 p-2 text-[11px] text-slate-300">
      <p className="font-medium text-white">{name ?? "Organisation"}</p>
      {address ? <p className="mt-1 text-slate-400">{address}</p> : null}
      {state ? <p className="text-slate-500">{state}</p> : null}
      {phone ? <p className="text-slate-500">{phone}</p> : null}
    </div>
  );
});
