# NPTTE Module Map

## Monorepo layout

| Path | Role | Phase 1 status |
|------|------|----------------|
| `backend/` | Django core, domain apps, API foundation | **Active** |
| `docs/` | Architecture, database, API, security, roadmap | **Active** |
| `web/` | Next.js TypeScript Tailwind citizen & operator UI | Placeholder |
| `mobile/` | Flutter Android/iOS apps | Placeholder |
| `ai-engine/` | Fraud detection, anomaly scoring | Placeholder |
| `blockchain-layer/` | Hyperledger Fabric audit anchoring | Placeholder |
| `infrastructure/` | Terraform, K8s, CI/CD | Placeholder |
| `frontend/` | Pre-existing directory (preserved) | Unchanged |

## Django application boundaries

### `apps.core`

Shared abstract models (`NPTTEBaseModel`), constants (`RecordStatus`, `AvailabilityStatus`, etc.), and permission placeholders. No business tables.

### `apps.accounts`

- **User** — Custom auth user (UUID PK, role, regulator flag)
- **Role** — Named platform roles

### `apps.organisations`

- **OrganisationType** — Manufacturer, pharmacy, regulator, etc.
- **Organisation** — Licensed entity with geolocation

### `apps.products`

- **Product** — Medicine master record
- **ProductBatch** — Batch-level traceability

### `apps.serialization`

- **ProductSerial** — Unit serial and QR payload

### `apps.inventory`

- **InventoryItem** — Stock at organisation
- **InventoryMovement** — Stock in/out events

### `apps.pharmacies`

- **PharmacyProfile** — Pharmacy-specific licensing and hours

### `apps.patients`

- **PatientProfile** — Patient identity and consent
- **MedicationSearchRequest** — Location-radius stock search
- **services.py** — `find_pharmacies_with_stock`, `process_medication_search` (placeholder logic)

### `apps.transactions`

- **PrescriptionUpload** — Prescription document reference
- **DispensingTransaction** — Dispense events

### `apps.verification`

- **VerificationEvent** — QR/SMS/web/mobile checks

### `apps.regulatory`

- **RegulatoryAlert** — Compliance and anomaly alerts

### `apps.audit`

- **AuditLog** — Append-only style audit records

### `apps.notifications`

- **Notification** — User notifications

## Cross-app dependencies

```
accounts.User
    └── organisations, patients, audit, notifications (FK)

organisations.Organisation
    └── products, inventory, pharmacies, transactions, regulatory

products.Product / ProductBatch
    └── serialization, inventory, patients, transactions

serialization.ProductSerial
    └── verification, transactions
```

## Integration points (future)

| Consumer | Provider | Mechanism |
|----------|----------|-----------|
| Web/Mobile | Backend | REST API (DRF), OpenAPI |
| FastAPI services | Backend | Internal REST / message bus |
| AI engine | verification, transactions | Event stream / batch export |
| Blockchain | audit | Async anchor jobs |
| NAFDAC systems | regulatory, products | Secure government API gateway |

## Naming conventions

- Apps: lowercase singular domain name (`patients`, not `patient`)
- Models: PascalCase singular (`MedicationSearchRequest`)
- Services: verb phrases in `services.py` per app when logic grows beyond models
