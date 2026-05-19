"""Phase 20A.2 — national operational demo dataset."""

DEMO_TYPE = "national_operational_demo"

NIGERIAN_LOCATIONS = [
    ("Lagos", "Ikeja", 6.5244, 3.3792),
    ("Abuja FCT", "Garki", 9.0579, 7.4951),
    ("Kano", "Nassarawa", 12.0022, 8.5920),
    ("Kaduna", "Central", 10.5105, 7.4165),
    ("Rivers", "Port Harcourt", 4.8156, 7.0498),
    ("Enugu", "New Haven", 6.4584, 7.5464),
    ("Oyo", "Ibadan", 7.3775, 3.9470),
    ("Ogun", "Abeokuta", 7.1608, 3.3481),
    ("Anambra", "Awka", 6.2109, 7.0743),
    ("Abia", "Umuahia", 5.5320, 7.4862),
    ("Edo", "Benin City", 6.3350, 5.6037),
    ("Delta", "Asaba", 6.1984, 6.7319),
    ("Sokoto", "Sokoto", 13.0059, 5.2476),
    ("Borno", "Maiduguri", 11.8311, 13.1510),
    ("Plateau", "Jos", 9.8965, 8.8583),
    ("Niger", "Minna", 9.6000, 6.5500),
    ("Cross River", "Calabar", 4.9517, 8.3220),
    ("Akwa Ibom", "Uyo", 5.0379, 7.9128),
    ("Benue", "Makurdi", 7.7319, 8.5391),
    ("Kwara", "Ilorin", 8.4966, 4.5421),
]

PRODUCT_CATALOG = [
    ("Amoxicillin", "antibiotic", "500mg", "capsule"),
    ("Artemether-Lumefantrine", "antimalarial", "20/120mg", "tablet"),
    ("Insulin Glargine", "cold_chain", "100IU/ml", "injection"),
    ("Paracetamol", "analgesic", "500mg", "tablet"),
    ("Metformin", "diabetes", "500mg", "tablet"),
    ("Amlodipine", "antihypertensive", "5mg", "tablet"),
    ("Azithromycin", "antibiotic", "500mg", "tablet"),
    ("ORS Zinc", "paediatric", "sachet", "powder"),
    ("BCG Vaccine", "vaccine", "0.05ml", "injection"),
    ("Tramadol", "controlled", "50mg", "capsule"),
    ("Salbutamol", "emergency", "100mcg", "inhaler"),
    ("Ceftriaxone", "antibiotic", "1g", "injection"),
    ("Losartan", "antihypertensive", "50mg", "tablet"),
    ("Glibenclamide", "diabetes", "5mg", "tablet"),
    ("Chloroquine", "antimalarial", "250mg", "tablet"),
]

STAFF_PROFILES = [
    ("Insp. Adebayo Okonkwo", "NAFDAC field inspector", "Lagos", "South West Inspection", "field_inspection"),
    ("Pharm. Maryam Bello", "Pharmacovigilance officer", "Kano", "North West PV Unit", "pharmacovigilance"),
    ("Dr. Chinedu Nwosu", "Recall desk officer", "Abuja FCT", "National Recall Desk", "recall"),
    ("Insp. Musa Ibrahim", "Customs liaison officer", "Lagos", "Apapa Customs Liaison", "customs"),
    ("Pharm. Tola Adebayo", "Regional supervisor", "Oyo", "South West Inspection", "inspection"),
    ("Dr. Fatima Abdullahi", "Intelligence analyst", "Kaduna", "North West Intelligence", "intelligence"),
    ("Insp. Grace Etim", "Cold-chain specialist", "Rivers", "Gulf Monitoring", "cold_chain"),
    ("Mr. Emeka Okafor", "Enforcement investigator", "Enugu", "South East Enforcement", "enforcement"),
    ("Mrs. Aisha Lawal", "Legal referral officer", "Abuja FCT", "Enforcement Legal", "legal"),
    ("Mr. Kunle Ajayi", "Logistics auditor", "Ogun", "National Logistics Audit", "logistics"),
]

EVENT_CATEGORIES = [
    ("suspicious_scan", "suspicious_scan", 120, "warning"),
    ("invalid_serial", "invalid_serial", 90, "high"),
    ("counterfeit_detection", "counterfeit", 75, "critical"),
    ("duplicate_serial", "duplicate_scan", 45, "high"),
    ("recall_non_ack", "recall_delay", 35, "high"),
    ("cold_chain_breach", "cold_chain", 30, "critical"),
    ("customs_hold", "customs_hold", 25, "high"),
    ("pharmacy_compliance", "compliance", 25, "medium"),
    ("manufacturer_serialization", "serialization", 20, "medium"),
    ("distributor_custody", "custody_gap", 20, "high"),
    ("warehouse_anomaly", "warehouse", 18, "medium"),
    ("expired_product", "expired", 15, "high"),
    ("citizen_report", "citizen_report", 15, "medium"),
    ("route_diversion", "diversion", 12, "high"),
    ("blacklisted_batch", "blacklist", 10, "critical"),
    ("shortage_alert", "shortage", 10, "critical"),
    ("emergency_recall", "emergency_recall", 8, "critical"),
    ("cross_state_counterfeit", "cluster_anomaly", 6, "critical"),
]


def demo_meta(**extra) -> dict:
    return {"demo_type": DEMO_TYPE, **extra}
