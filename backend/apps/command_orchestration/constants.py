"""Phase 20C — regional zones, map layers, streambus scopes."""
from __future__ import annotations

MAP_LAYERS = frozenset(
    {
        "operational",
        "counterfeit",
        "recalls",
        "shortage",
        "investigations",
        "enforcement",
        "customs",
    }
)

REGIONS = {
    "south_west": {
        "label": "South West",
        "states": ["Lagos", "Oyo", "Ogun"],
    },
    "south_east": {
        "label": "South East",
        "states": ["Enugu", "Anambra", "Abia"],
    },
    "south_south": {
        "label": "South South",
        "states": ["Rivers", "Delta", "Edo", "Cross River", "Akwa Ibom"],
    },
    "north_central": {
        "label": "North Central",
        "states": ["Abuja FCT", "Plateau", "Niger", "Benue", "Kwara"],
    },
    "north_east": {
        "label": "North East",
        "states": ["Borno"],
    },
    "north_west": {
        "label": "North West",
        "states": ["Kano", "Kaduna", "Sokoto"],
    },
}

STREAM_CHANNELS = frozenset(
    {
        "national",
        "regional",
        "investigation",
        "escalation",
        "officer_tasks",
        "executive",
    }
)
