# NPTTE RBAC Matrix (Phase 4)

| Role | Auth | Pharmacy | Patient | Manufacturer | Regulator dashboard | Verify (public) |
|------|------|----------|---------|--------------|---------------------|-----------------|
| SUPER_ADMIN | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| NAFDAC_ADMIN / NDLEA / PCN / NHIA / FMOH | ✓ | read | read | read | ✓ | ✓ |
| MANUFACTURER | ✓ | — | — | ✓ | — | ✓ |
| PHARMACY_* | ✓ | ✓ | — | — | — | ✓ |
| PATIENT | ✓ | — | ✓ | — | — | ✓ |
| AUDITOR | ✓ | read | read | read | ✓ | ✓ |

Legacy codes (`PHARMACY_ADMIN`, `PHARMACIST`, etc.) remain valid alongside expanded codes (`PHARMACY_OWNER`, `NATIONAL_REGULATOR`, …).
