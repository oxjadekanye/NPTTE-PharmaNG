"use client";

import { memo } from "react";

export const ExplorerProductCard = memo(function ExplorerProductCard({
  product,
  batch,
  serial,
}: {
  product?: string;
  batch?: string;
  serial?: string;
}) {
  return (
    <div className="rounded border border-sovereign-800 p-2 text-[11px] text-slate-300">
      <p className="font-medium text-white">{product ?? "Product"}</p>
      {batch ? <p className="mt-1">Batch: {batch}</p> : null}
      {serial ? <p className="text-slate-500">Serial: {serial}</p> : null}
    </div>
  );
});
