import { apiRequest } from "./api-client";

export type CopilotPayload = {
  summary: string;
  reasoning: string;
  recommended_actions: string[];
  urgency: string;
  confidence: number;
  source_records: Record<string, unknown>[];
  human_review_required: boolean;
  disclaimer: string;
  source?: string;
  mode?: string;
  cached?: boolean;
};

export type CopilotRequest = {
  entity_type?: string;
  entity_id?: string;
  context_key?: string;
  selected_record_ids?: string[];
  prompt_mode?: string;
  user_question?: string;
};

const COPILOT_CACHE_MS = 10 * 60 * 1000;
const mem = new Map<string, { at: number; data: CopilotPayload }>();

function cacheKey(endpoint: string, body: CopilotRequest): string {
  return `${endpoint}:${JSON.stringify(body)}`;
}

function readCache(key: string): CopilotPayload | null {
  const hit = mem.get(key);
  if (hit && Date.now() - hit.at < COPILOT_CACHE_MS) return hit.data;
  return null;
}

function writeCache(key: string, data: CopilotPayload) {
  mem.set(key, { at: Date.now(), data });
}

async function postCopilot(path: string, body: CopilotRequest) {
  const key = cacheKey(path, body);
  const cached = readCache(key);
  if (cached) {
    return { success: true as const, data: { ...cached, cached: true } };
  }
  const res = await apiRequest<CopilotPayload>(`/copilot/${path}`, {
    method: "POST",
    body: JSON.stringify(body),
  });
  if (res.success && res.data) {
    writeCache(key, res.data);
  }
  return res;
}

export function copilotExplainRisk(body: CopilotRequest) {
  return postCopilot("explain-risk/", { ...body, prompt_mode: "explain_risk" });
}

export function copilotGenerateBriefing(body: CopilotRequest) {
  return postCopilot("generate-briefing/", { ...body, prompt_mode: "generate_briefing" });
}

export function copilotRecommendActions(body: CopilotRequest) {
  return postCopilot("recommend-actions/", { ...body, prompt_mode: "recommend_actions" });
}

export function copilotSummariseInvestigation(body: CopilotRequest) {
  return postCopilot("summarise-investigation/", { ...body, prompt_mode: "summarise_investigation" });
}

export function copilotDraftEnforcementNote(body: CopilotRequest) {
  return postCopilot("draft-enforcement-note/", { ...body, prompt_mode: "draft_enforcement_note" });
}

export function copilotExecutiveBriefing(userQuestion?: string) {
  return postCopilot("executive-briefing/", {
    context_key: "national_status",
    prompt_mode: "executive_briefing",
    user_question: userQuestion,
  });
}
