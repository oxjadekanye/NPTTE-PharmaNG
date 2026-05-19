"use client";

import { CopilotPanel } from "./CopilotPanel";
import {
  copilotDraftEnforcementNote,
  copilotRecommendActions,
  copilotSummariseInvestigation,
  type CopilotRequest,
} from "@/services/copilot";

const ENFORCEMENT_ACTIONS = [
  { id: "summarise", label: "Summarise case", run: copilotSummariseInvestigation },
  {
    id: "next_step",
    label: "Suggest next investigative step",
    run: (body: CopilotRequest) =>
      copilotRecommendActions({
        ...body,
        user_question: "What is the next investigative step for this enforcement case?",
      }),
  },
  { id: "note", label: "Draft enforcement note", run: copilotDraftEnforcementNote },
  {
    id: "inspection",
    label: "Draft inspection assignment",
    run: (body: CopilotRequest) =>
      copilotRecommendActions({
        ...body,
        user_question: "Draft inspection assignment with site, scope, and timeline.",
      }),
  },
];

export function EnforcementCopilotPanel({ caseId }: { caseId: string }) {
  return (
    <CopilotPanel
      compact
      entityType="enforcement_case"
      entityId={caseId}
      extraActions={ENFORCEMENT_ACTIONS}
    />
  );
}
