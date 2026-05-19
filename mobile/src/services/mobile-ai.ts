import { apiRequest } from "@/services/api-client";

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
}) {
  const question =
    body.user_question ??
    (body.serial_number ? `Explain scan result for serial ${body.serial_number}` : undefined);
  return apiRequest<Record<string, unknown>>("/mobile/copilot/", {
    method: "POST",
    body: JSON.stringify({ ...body, user_question: question }),
  });
}
