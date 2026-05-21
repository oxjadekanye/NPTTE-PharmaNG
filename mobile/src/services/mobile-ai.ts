import { apiRequest } from "@/services/api-client";

export {
  checklistFallbackRecommendation,
  parseCopilotText,
} from "@/services/mobile-ai-helpers";

export type MobileAiMode =
  | "explain_risk"
  | "recommend_actions"
  | "summarise_investigation"
  | "draft_enforcement_note"
  | "operational_recommendations";

export async function mobileCopilot(body: {
  prompt_mode: MobileAiMode;
  entity_type?: string;
  entity_id?: string;
  context_key?: string;
  user_question?: string;
  serial_number?: string;
  inspection_context?: Record<string, unknown>;
}) {
  const question =
    body.user_question ??
    (body.serial_number ? `Explain scan result for serial ${body.serial_number}` : undefined);
  return apiRequest<Record<string, unknown>>("/mobile/copilot/", {
    method: "POST",
    body: JSON.stringify({ ...body, user_question: question }),
  });
}

export async function mobileInspectionCopilot(inspectionContext: Record<string, unknown>) {
  const score = inspectionContext.compliance_score ?? 0;
  return mobileCopilot({
    prompt_mode: "operational_recommendations",
    context_key: "field_inspection",
    user_question: `Field inspection recommendation for score ${score}% with failed items: ${JSON.stringify(inspectionContext.failed_items ?? [])}`,
    inspection_context: inspectionContext,
  });
}
