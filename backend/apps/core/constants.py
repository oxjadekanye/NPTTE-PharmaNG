"""
Shared constants for NPTTE domain models.

Centralised status and category values keep cross-app references consistent.
"""

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
