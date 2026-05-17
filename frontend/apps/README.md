# NPTTE Frontend Apps (Logical Modules)

Modular apps map to Next.js App Router routes under `src/app/`:

| Module | Route prefix | Purpose |
|--------|--------------|---------|
| `regulator-dashboard` | `/regulator` | National overview & metrics |
| `command-center` | `/command-center` | Threat map, incidents, approvals |
| `citizen-portal` | `/citizen` | Public verification & reporting |
| `emergency-ops` | `/emergency-ops` | Crisis distribution controls |

Shared code: `src/components/`, `src/services/`, `src/hooks/`, `src/store/`, `src/realtime/`.
