import { redirect } from "next/navigation";

const DEFAULT_TYPE: Record<string, string> = {
  "national-risk-current": "national_risk",
  "high-risk-current": "national_risk",
  "open-alerts-current": "alert",
  "fraud-flags-current": "national_risk",
  "counterfeit-detections-current": "national_risk",
  "active-investigations-current": "national_risk",
  "products-tracked-current": "product",
  "recalls-current": "national_risk",
  "command-activity-current": "task",
};

export default async function ExplorerAggregateRedirectPage({
  params,
}: {
  params: Promise<{ aggregateId: string }>;
}) {
  const { aggregateId: raw } = await params;
  const aggregateId = decodeURIComponent(raw);
  const entityType = DEFAULT_TYPE[aggregateId] ?? "national_risk";
  redirect(`/regulator/explorer/${encodeURIComponent(entityType)}/${encodeURIComponent(aggregateId)}`);
}
