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
    # Phase 3 — expanded national RBAC (legacy codes retained for compatibility)
    NATIONAL_REGULATOR = "NATIONAL_REGULATOR"
    STATE_REGULATOR = "STATE_REGULATOR"
    WAREHOUSE_MANAGER = "WAREHOUSE_MANAGER"
    PHARMACY_OWNER = "PHARMACY_OWNER"
    PHARMACY_STAFF = "PHARMACY_STAFF"
    PCN_ADMIN = "PCN_ADMIN"
    NHIA_ADMIN = "NHIA_ADMIN"
    FMOH_ADMIN = "FMOH_ADMIN"

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
        (NATIONAL_REGULATOR, "National regulator"),
        (STATE_REGULATOR, "State regulator"),
        (WAREHOUSE_MANAGER, "Warehouse manager"),
        (PHARMACY_OWNER, "Pharmacy owner"),
        (PHARMACY_STAFF, "Pharmacy staff"),
        (PCN_ADMIN, "PCN regulator admin"),
        (NHIA_ADMIN, "NHIA regulator admin"),
        (FMOH_ADMIN, "Federal Ministry of Health admin"),
    ]

    REGULATOR_CODES = frozenset({
        SUPER_ADMIN,
        NAFDAC_ADMIN,
        NDLEA_ADMIN,
        AUDITOR,
        NATIONAL_REGULATOR,
        STATE_REGULATOR,
        PCN_ADMIN,
        NHIA_ADMIN,
        FMOH_ADMIN,
    })

    PHARMACY_CODES = frozenset({
        PHARMACY_ADMIN,
        PHARMACIST,
        PHARMACY_OWNER,
        PHARMACY_STAFF,
    })

    SUPPLY_CHAIN_CODES = frozenset({DISTRIBUTOR, MANUFACTURER, LOGISTICS})

    HOSPITAL_CODES = frozenset({HOSPITAL_ADMIN, DOCTOR})

    SELF_REGISTER_CODES = frozenset({PATIENT, PHARMACIST})

    ALL_CODES = frozenset(code for code, _ in CHOICES)


class SupplyChainTransactionType:
    """National pharmaceutical movement and lifecycle events."""

    MEDICATION_CREATED = "medication_created"
    BATCH_CREATED = "batch_created"
    MANUFACTURER_DISPATCH = "manufacturer_dispatch"
    WAREHOUSE_RECEIPT = "warehouse_receipt"
    WAREHOUSE_TRANSFER = "warehouse_transfer"
    DISTRIBUTOR_RECEIPT = "distributor_receipt"
    DISTRIBUTOR_DISPATCH = "distributor_dispatch"
    PHARMACY_STOCKING = "pharmacy_stocking"
    PHARMACY_SALE = "pharmacy_sale"
    PRESCRIPTION_ISSUED = "prescription_issued"
    PATIENT_PURCHASE = "patient_purchase"
    STOCK_DEPLETION = "stock_depletion"
    STOCK_ADJUSTMENT = "stock_adjustment"
    RETURN = "return"
    RECALL = "recall"
    DESTROYED = "destroyed"
    EXPIRED = "expired"

    CHOICES = [
        (MEDICATION_CREATED, "Medication created"),
        (BATCH_CREATED, "Batch created"),
        (MANUFACTURER_DISPATCH, "Manufacturer dispatch"),
        (WAREHOUSE_RECEIPT, "Warehouse receipt"),
        (WAREHOUSE_TRANSFER, "Warehouse transfer"),
        (DISTRIBUTOR_RECEIPT, "Distributor receipt"),
        (DISTRIBUTOR_DISPATCH, "Distributor dispatch"),
        (PHARMACY_STOCKING, "Pharmacy stocking"),
        (PHARMACY_SALE, "Pharmacy sale"),
        (PRESCRIPTION_ISSUED, "Prescription issued"),
        (PATIENT_PURCHASE, "Patient purchase"),
        (STOCK_DEPLETION, "Stock depletion"),
        (STOCK_ADJUSTMENT, "Stock adjustment"),
        (RETURN, "Return"),
        (RECALL, "Recall"),
        (DESTROYED, "Destroyed stock"),
        (EXPIRED, "Expired medication"),
    ]


class VerificationStatus:
    PENDING = "pending"
    VERIFIED = "verified"
    SUSPICIOUS = "suspicious"
    FAILED = "failed"
    RECALLED = "recalled"

    CHOICES = [
        (PENDING, "Pending"),
        (VERIFIED, "Verified"),
        (SUSPICIOUS, "Suspicious"),
        (FAILED, "Failed"),
        (RECALLED, "Recalled"),
    ]


class VerificationOutcome:
    """Sovereign verification engine outcomes."""

    AUTHENTIC = "authentic"
    COUNTERFEIT_SUSPECTED = "counterfeit_suspected"
    RECALLED = "recalled"
    EXPIRED = "expired"
    DUPLICATE_SCAN_DETECTED = "duplicate_scan_detected"
    INVALID_SERIAL = "invalid_serial"
    UNREGISTERED_PRODUCT = "unregistered_product"

    CHOICES = [
        (AUTHENTIC, "Authentic"),
        (COUNTERFEIT_SUSPECTED, "Counterfeit suspected"),
        (RECALLED, "Recalled"),
        (EXPIRED, "Expired"),
        (DUPLICATE_SCAN_DETECTED, "Duplicate scan detected"),
        (INVALID_SERIAL, "Invalid serial"),
        (UNREGISTERED_PRODUCT, "Unregistered product"),
    ]


class ShipmentLifecycle:
    CREATED = "created"
    IN_TRANSIT = "in_transit"
    ARRIVED = "arrived"
    VERIFIED = "verified"
    REJECTED = "rejected"
    LOST = "lost"
    RECALLED = "recalled"

    CHOICES = [
        (CREATED, "Created"),
        (IN_TRANSIT, "In transit"),
        (ARRIVED, "Arrived"),
        (VERIFIED, "Verified"),
        (REJECTED, "Rejected"),
        (LOST, "Lost"),
        (RECALLED, "Recalled"),
    ]


class AlertCategory:
    COUNTERFEIT = "counterfeit"
    RECALL = "recall"
    DIVERSION = "diversion"
    THEFT = "theft"
    EXPIRY_RISK = "expiry_risk"
    UNUSUAL_SALES_SPIKE = "unusual_sales_spike"
    SUSPICIOUS_WAREHOUSE = "suspicious_warehouse_activity"
    COLD_CHAIN_BREACH = "cold_chain_breach"
    VERIFICATION_ANOMALY = "verification_anomaly"
    SHORTAGE = "shortage"

    CHOICES = [
        (COUNTERFEIT, "Counterfeit"),
        (RECALL, "Recall"),
        (DIVERSION, "Diversion"),
        (THEFT, "Theft"),
        (EXPIRY_RISK, "Expiry risk"),
        (UNUSUAL_SALES_SPIKE, "Unusual sales spike"),
        (SUSPICIOUS_WAREHOUSE, "Suspicious warehouse activity"),
        (COLD_CHAIN_BREACH, "Cold chain breach"),
        (VERIFICATION_ANOMALY, "Verification anomaly"),
        (SHORTAGE, "Shortage"),
    ]


class RegulatorBatchStatus:
    PENDING = "pending"
    APPROVED = "approved"
    SUSPENDED = "suspended"
    REJECTED = "rejected"

    CHOICES = [
        (PENDING, "Pending"),
        (APPROVED, "Approved"),
        (SUSPENDED, "Suspended"),
        (REJECTED, "Rejected"),
    ]


class BatchLifecycleStatus:
    """
    National batch lifecycle for serialization and circulation (Phase 8).

    Parallel to regulator_status: lifecycle tracks manufacturing/circulation state.
    """

    DRAFT = "draft"
    APPROVED = "approved"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    RECALLED = "recalled"
    EXPIRED = "expired"
    DESTROYED = "destroyed"

    CHOICES = [
        (DRAFT, "Draft"),
        (APPROVED, "Approved"),
        (ACTIVE, "Active"),
        (SUSPENDED, "Suspended"),
        (RECALLED, "Recalled"),
        (EXPIRED, "Expired"),
        (DESTROYED, "Destroyed"),
    ]


class BatchRegulatoryAuditAction:
    """Immutable audit actions for regulator–batch interactions (Phase 8)."""

    SUBMITTED = "submitted"
    APPROVED = "approved"
    REJECTED = "rejected"
    SUSPENDED = "suspended"
    RECALLED = "recalled"
    SERIALS_ISSUED = "serials_issued"
    DESTROYED = "destroyed"

    CHOICES = [
        (SUBMITTED, "Submitted for approval"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
        (SUSPENDED, "Suspended"),
        (RECALLED, "Recalled"),
        (SERIALS_ISSUED, "Serials issued"),
        (DESTROYED, "Destroyed"),
    ]


class RiskLevel:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    CHOICES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (CRITICAL, "Critical"),
    ]


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


# Phase 5 — national command platform
class IncidentSeverity:
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

    CHOICES = [
        (LOW, "Low"),
        (MEDIUM, "Medium"),
        (HIGH, "High"),
        (CRITICAL, "Critical"),
    ]


class IncidentStatus:
    OPEN = "open"
    INVESTIGATING = "investigating"
    CONTAINED = "contained"
    RESOLVED = "resolved"

    CHOICES = [
        (OPEN, "Open"),
        (INVESTIGATING, "Investigating"),
        (CONTAINED, "Contained"),
        (RESOLVED, "Resolved"),
    ]


class EventCategory:
    SYSTEM = "system"
    VERIFICATION = "verification"
    INVENTORY = "inventory"
    EMERGENCY = "emergency"
    FRAUD = "fraud"

    CHOICES = [
        (SYSTEM, "System"),
        (VERIFICATION, "Verification"),
        (INVENTORY, "Inventory"),
        (EMERGENCY, "Emergency"),
        (FRAUD, "Fraud"),
    ]


class OnboardingStatus:
    DRAFT = "draft"
    SUBMITTED = "submitted"
    UNDER_REVIEW = "under_review"
    APPROVED = "approved"
    REJECTED = "rejected"

    CHOICES = [
        (DRAFT, "Draft"),
        (SUBMITTED, "Submitted"),
        (UNDER_REVIEW, "Under review"),
        (APPROVED, "Approved"),
        (REJECTED, "Rejected"),
    ]


class EmergencyMode:
    NORMAL = "normal"
    ELEVATED = "elevated"
    CRISIS = "crisis"

    CHOICES = [
        (NORMAL, "Normal"),
        (ELEVATED, "Elevated"),
        (CRISIS, "Crisis"),
    ]
