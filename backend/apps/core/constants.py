"""
Shared constants for NPTTE domain models.

Centralised status and category values keep cross-app references consistent.
"""


class RoleCode:
    """Platform role codes for RBAC across regulators, supply chain, and patients."""

    SUPER_ADMIN = "SUPER_ADMIN"
    NAFDAC_ADMIN = "NAFDAC_ADMIN"
    NDLEA_ADMIN = "NDLEA_ADMIN"
    PHARMACY_ADMIN = "PHARMACY_ADMIN"
    PHARMACIST = "PHARMACIST"
    HOSPITAL_ADMIN = "HOSPITAL_ADMIN"
    DOCTOR = "DOCTOR"
    DISTRIBUTOR = "DISTRIBUTOR"
    MANUFACTURER = "MANUFACTURER"
    LOGISTICS = "LOGISTICS"
    PATIENT = "PATIENT"
    AUDITOR = "AUDITOR"

    CHOICES = [
        (SUPER_ADMIN, "Super administrator"),
        (NAFDAC_ADMIN, "NAFDAC regulator admin"),
        (NDLEA_ADMIN, "NDLEA regulator admin"),
        (PHARMACY_ADMIN, "Pharmacy administrator"),
        (PHARMACIST, "Pharmacist"),
        (HOSPITAL_ADMIN, "Hospital administrator"),
        (DOCTOR, "Doctor"),
        (DISTRIBUTOR, "Distributor"),
        (MANUFACTURER, "Manufacturer"),
        (LOGISTICS, "Logistics provider"),
        (PATIENT, "Patient"),
        (AUDITOR, "Auditor"),
    ]

    REGULATOR_CODES = frozenset({SUPER_ADMIN, NAFDAC_ADMIN, NDLEA_ADMIN, AUDITOR})

    PHARMACY_CODES = frozenset({PHARMACY_ADMIN, PHARMACIST})

    SUPPLY_CHAIN_CODES = frozenset({DISTRIBUTOR, MANUFACTURER, LOGISTICS})

    HOSPITAL_CODES = frozenset({HOSPITAL_ADMIN, DOCTOR})

    SELF_REGISTER_CODES = frozenset({PATIENT, PHARMACIST})

    ALL_CODES = frozenset(code for code, _ in CHOICES)

# Generic record lifecycle
class RecordStatus:
    DRAFT = "draft"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    ARCHIVED = "archived"

    CHOICES = [
        (DRAFT, "Draft"),
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (ARCHIVED, "Archived"),
    ]


# Inventory availability (foundation — extended in later phases)
class AvailabilityStatus:
    IN_STOCK = "in_stock"
    LOW_STOCK = "low_stock"
    OUT_OF_STOCK = "out_of_stock"
    RESERVED = "reserved"

    CHOICES = [
        (IN_STOCK, "In stock"),
        (LOW_STOCK, "Low stock"),
        (OUT_OF_STOCK, "Out of stock"),
        (RESERVED, "Reserved"),
    ]


# Medication search request lifecycle (patient-facing feature foundation)
class MedicationSearchStatus:
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

    CHOICES = [
        (PENDING, "Pending"),
        (PROCESSING, "Processing"),
        (COMPLETED, "Completed"),
        (FAILED, "Failed"),
    ]


# Verification channel foundation
class VerificationChannel:
    QR = "qr"
    SMS = "sms"
    WEB = "web"
    MOBILE = "mobile"

    CHOICES = [
        (QR, "QR code"),
        (SMS, "SMS"),
        (WEB, "Web"),
        (MOBILE, "Mobile app"),
    ]


# Regulatory alert severity
class AlertSeverity:
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"

    CHOICES = [
        (INFO, "Information"),
        (WARNING, "Warning"),
        (CRITICAL, "Critical"),
    ]
