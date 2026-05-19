import { apiRequest } from "@/services/api-client";

export async function fetchCommandRoomSnapshot() {
  return apiRequest<Record<string, unknown>>("/command-orchestration/command-room/");
}

export async function fetchRegionalList() {
  return apiRequest<{ regions: { key: string; label: string }[] }>("/command-orchestration/regions/");
}

export async function fetchExecutiveBriefing() {
  return apiRequest<Record<string, unknown>>("/copilot/executive-briefing/", {
    method: "POST",
    body: JSON.stringify({ context_key: "national_status", prompt_mode: "executive_briefing" }),
  });
}
