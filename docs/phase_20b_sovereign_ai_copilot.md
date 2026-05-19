# Phase 20B — Sovereign AI Copilot + Operational Reasoning Layer

## Overview

On-demand AI assistance for regulators: risk explanation, briefings, action recommendations, investigation summaries, and enforcement notes. **No automatic AI on page load.** Every response includes human-review disclaimers and uses deterministic fallback when OpenAI is unavailable or times out.

## APIs (POST, regulator JWT)

| Endpoint | Mode | Purpose |
|----------|------|---------|
| `/api/v1/copilot/explain-risk/` | `explain_risk` | Explain operational risk for entity/context |
| `/api/v1/copilot/generate-briefing/` | `generate_briefing` | Operational briefing |
| `/api/v1/copilot/recommend-actions/` | `recommend_actions` | Recommended regulator actions |
| `/api/v1/copilot/summarise-investigation/` | `summarise_investigation` | Investigation summary |
| `/api/v1/copilot/draft-enforcement-note/` | `draft_enforcement_note` | Draft enforcement note |
| `/api/v1/copilot/executive-briefing/` | `executive_briefing` | National ministerial briefing |

### Request body

```json
{
  "entity_type": "enforcement_case",
  "entity_id": "<uuid>",
  "context_key": "national_status",
  "selected_record_ids": ["optional-record-id"],
  "prompt_mode": "explain_risk",
  "user_question": "optional free text"
}
```

Provide either `context_key` or `entity_type` + `entity_id`.

### Response

```json
{
  "summary": "...",
  "reasoning": "...",
  "recommended_actions": ["..."],
  "urgency": "high",
  "confidence": 0.72,
  "source_records": [],
  "human_review_required": true,
  "disclaimer": "AI-assisted recommendation — requires human review.",
  "source": "deterministic|openai|deterministic_fallback"
}
```

## Backend layout

- `apps/copilot/constants.py` — timeouts (10s), cache TTL (600s), disclaimer
- `apps/copilot/services/provider.py` — OpenAI adapter (thread pool + timeout)
- `apps/copilot/services/sanitizer.py` — context sanitisation
- `apps/copilot/services/source_records.py` — grounded source records
- `apps/copilot/services/context_loader.py` — tenant-safe explorer bundle load
- `apps/copilot/services/reasoning.py` — orchestration + deterministic fallback
- `apps/copilot/services/cache.py` — Redis/in-memory 10-minute cache

## UI

| Location | Component |
|----------|-----------|
| Explorer drawer / entity detail | `CopilotPanel` (click-to-run) |
| Executive mode | `ExecutiveAiBriefingPanel` (compact) |
| `/executive/ai-briefing` | Full executive AI briefing workspace |
| Enforcement cases | `EnforcementCopilotPanel` per case |

Buttons never auto-fire; loading states are local to the panel.

## Safety

- `human_review_required: true` on every response
- AI does **not** execute enforcement or explorer actions
- RBAC via explorer access checks (`_check_explorer_access`)
- API keys only in server env (`OPENAI_API_KEY`)

## Performance

- OpenAI timeout: 10 seconds (configurable via `OPENAI_TIMEOUT_SEC`)
- Server cache: 10 minutes per user/mode/context
- Client memory cache: 10 minutes per endpoint payload
- UI remains non-blocking; panels show loading only inside copilot section

## Deployment notes

1. Set `OPENAI_API_KEY` (and optional `OPENAI_MODEL`, default `gpt-4o-mini`) on Render.
2. Ensure `REDIS_URL` for shared copilot cache across workers.
3. Deploy backend + frontend together.
4. No migrations required for copilot app.
5. Optional: `python manage.py warm_explorer_cache` for faster first copilot context load.

## Tests

```bash
cd backend && python manage.py check
USE_SQLITE=1 python manage.py test tests.test_phase20b_copilot
cd frontend && npm run build && npm test
```

## Limitations

- OpenAI JSON schema is best-effort; malformed responses fall back to deterministic text.
- Executive briefing uses `national_status` context; region granularity depends on seeded demo data.
- No streaming responses; single-shot completion only.
- Copilot does not persist chat history or multi-turn threads.
- Inspection assignment drafting reuses `recommend_actions` with a guided `user_question`.
