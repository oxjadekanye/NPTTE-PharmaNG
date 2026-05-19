"""Phase 20B — sovereign AI copilot constants."""
from __future__ import annotations

DISCLAIMER = "AI-assisted recommendation — requires human review."
HUMAN_REVIEW_REQUIRED = True

OPENAI_TIMEOUT_SEC = 10
COPILOT_CACHE_TTL_SEC = 600  # 10 minutes

PROMPT_MODES = frozenset(
    {
        "explain_risk",
        "generate_briefing",
        "recommend_actions",
        "summarise_investigation",
        "draft_enforcement_note",
        "executive_briefing",
    }
)
