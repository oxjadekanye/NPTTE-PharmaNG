export function parseCopilotText(data: Record<string, unknown> | undefined): string | null {
  if (!data) return null;
  const summary = data.summary;
  const reasoning = data.reasoning;
  const parts: string[] = [];
  if (typeof summary === "string" && summary.trim()) parts.push(summary.trim());
  else if (summary && typeof summary === "object") {
    const s = summary as Record<string, unknown>;
    const title = s.title ?? s.body;
    if (typeof title === "string" && title.trim()) parts.push(title.trim());
  }
  if (typeof reasoning === "string" && reasoning.trim()) parts.push(reasoning.trim());
  if (parts.length) return parts.join("\n\n");
  if (typeof data.message === "string" && data.message.trim()) return data.message.trim();
  return null;
}

export function checklistFallbackRecommendation(score: number): string {
  if (score >= 80) {
    return (
      "Checklist largely complete. Maintain documented custody chain and batch records. " +
      "Escalate only if serial mismatch recurs on re-scan or cold-chain gaps appear."
    );
  }
  if (score >= 50) {
    return (
      "Partial compliance. Prioritize batch record review, cold-chain logs, and staff interviews. " +
      "Schedule follow-up inspection within 7 days and document corrective actions."
    );
  }
  return (
    "Low compliance score. Immediate field actions: quarantine suspect stock, collect serial samples, " +
    "verify recall acknowledgement, and notify regional enforcement coordinator."
  );
}
