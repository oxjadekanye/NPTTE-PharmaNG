"""Phase 13 — national traceability walkthrough demo identifiers."""

DEMO_TYPE = "traceability_demo"

# Citizen-facing test serials (invalid is not stored in registry)
SERIAL_AUTHENTIC = "NG-NPTTE-TD-PARACETAMOL-2026-AUTH000001"
SERIAL_RECALLED = "NG-NPTTE-TD-AMOXICILLIN-2026-RECALL000001"
SERIAL_SUSPICIOUS = "NG-NPTTE-TD-METFORMIN-2026-SUSPIC000001"
SERIAL_EXPIRED = "NG-NPTTE-TD-PARACETAMOL-2025-EXP0000001"
SERIAL_INVALID = "NG-NPTTE-TD-INVALID-000000001"

DEMO_SERIALS = {
    "authentic": SERIAL_AUTHENTIC,
    "recalled": SERIAL_RECALLED,
    "suspicious": SERIAL_SUSPICIOUS,
    "expired": SERIAL_EXPIRED,
    "invalid": SERIAL_INVALID,
}


def demo_meta(**extra) -> dict:
    return {"demo_type": DEMO_TYPE, **extra}
