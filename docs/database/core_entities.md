# Core Database Entities

Phase 1 foundational entities. All domain models (except `User`, `Role`, `AuditLog`) inherit **`NPTTEBaseModel`** fields where applicable.

## Shared base fields (`NPTTEBaseModel`)

| Field | Type | Purpose |
|-------|------|---------|
| `id` | UUID | Stable distributed identifier |
| `created_at` | datetime | Record creation (indexed) |
| `updated_at` | datetime | Last modification |
| `created_by` | FK → User | Acting user (nullable) |
| `is_active` | boolean | Soft operational flag |
| `status` | string | Lifecycle: draft, active, suspended, archived |
| `metadata` | JSON | Integration extensions |

## Entity catalogue

### Identity

| Model | App | Key relationships |
|-------|-----|-------------------|
| User | accounts | → Role |
| Role | accounts | — |

### Organisations

| Model | App | Key relationships |
|-------|-----|-------------------|
| OrganisationType | organisations | — |
| Organisation | organisations | → OrganisationType |
| PharmacyProfile | pharmacies | → Organisation (1:1) |

### Products & serialization

| Model | App | Key relationships |
|-------|-----|-------------------|
| Product | products | → Organisation (manufacturer) |
| ProductBatch | products | → Product |
| ProductSerial | serialization | → ProductBatch |

### Inventory

| Model | App | Key relationships |
|-------|-----|-------------------|
| InventoryItem | inventory | → Organisation, Product, ProductBatch? |
| InventoryMovement | inventory | → InventoryItem |

### Patients

| Model | App | Key relationships |
|-------|-----|-------------------|
| PatientProfile | patients | → User? |
| MedicationSearchRequest | patients | → Patient?, Product |

**Medication search:** Stores `latitude`, `longitude`, `radius_miles`, and `results_snapshot` JSON. Service layer matches pharmacies with `InventoryItem.availability_status = in_stock` within radius.

### Transactions

| Model | App | Key relationships |
|-------|-----|-------------------|
| PrescriptionUpload | transactions | → Patient?, Organisation (pharmacy) |
| DispensingTransaction | transactions | → Pharmacy, Patient?, Product, ProductSerial?, PrescriptionUpload? |

### Verification & regulatory

| Model | App | Key relationships |
|-------|-----|-------------------|
| VerificationEvent | verification | → ProductSerial |
| RegulatoryAlert | regulatory | → Organisation? |

### Platform

| Model | App | Key relationships |
|-------|-----|-------------------|
| AuditLog | audit | → User (actor) |
| Notification | notifications | → User (recipient) |

## Indexing strategy (Phase 1)

- UUID primary keys on all major entities
- `created_at`, `status`, `is_active` indexed via base model
- Foreign keys indexed by Django default
- Composite index on `InventoryItem (organisation, product, availability_status)`
- Composite index on `AuditLog (entity_type, entity_id)`

## Future database work

- PostGIS for geospatial pharmacy search at national scale
- Partitioning for `AuditLog` and `VerificationEvent` high-volume tables
- Read replicas for patient search and public verification
- Field-level encryption for PII (patient phone, national ID)
