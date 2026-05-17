# NPTTE — National Pharmaceutical Transparency & Traceability Ecosystem

**NPTTE** is Nigeria’s national-scale platform for pharmaceutical transparency, medicine traceability, and public health supply chain integrity. It is designed to support medicine serialization, pharmacy registration, patient medication discovery, real-time inventory visibility, QR verification, regulatory oversight, and— in later phases— AI-assisted fraud detection and blockchain-anchored audit trails.

## Purpose

NPTTE provides a secure, modular foundation for:

- Tracking medicines from manufacture/import through distribution to dispensing
- Registering and licensing organisations across the supply chain
- Enabling patients to find medicines in stock at nearby registered pharmacies
- Supporting regulators with alerts, inspections, and audit visibility
- Verifying medicine authenticity via serial numbers and QR identities

## Current phase: **Phase 1 — Backend foundation**

This repository phase establishes:

- Django monorepo structure and domain applications
- Foundational database models and admin registration
- Architecture and security documentation
- Placeholder directories for web, mobile, AI, and blockchain (not implemented)

**Not yet implemented:** REST API endpoints, authentication flows, Next.js web dashboard, Flutter mobile apps, FastAPI microservices, AI fraud detection, Hyperledger Fabric, production infrastructure, and real-time inventory sync.

## Repository structure

```
NPTTE-PharmaNG/
├── backend/                 # Django + DRF core API foundation
│   ├── apps/                # Domain Django applications
│   ├── config/              # Project settings and URLs
│   ├── requirements.txt
│   └── .env.example
├── docs/                    # Architecture, API, security, roadmap
├── web/                     # Future Next.js platform (placeholder)
├── mobile/                  # Future Flutter apps (placeholder)
├── frontend/                # Legacy/existing folder (preserved)
├── ai-engine/               # Future Python AI services (placeholder)
├── blockchain-layer/        # Future Hyperledger Fabric (placeholder)
└── infrastructure/          # Future IaC and deployment (placeholder)
```

See [docs/architecture/module_map.md](docs/architecture/module_map.md) for module responsibilities.

## Local setup

### Prerequisites

- Python 3.10+ (3.11+ recommended; Django 4.2 LTS supports 3.9+)
- PostgreSQL 14+ (recommended) **or** SQLite for quick bootstrap
- `virtualenv` or `venv`

### 1. Virtual environment

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Environment variables

```bash
cp .env.example .env
```

Edit `backend/.env`:

- For **PostgreSQL**: set `DB_*` values and `USE_SQLITE=False`
- For **quick local bootstrap**: set `USE_SQLITE=True`

Generate a strong `SECRET_KEY` before any shared or production use.

### 3. Database and migrations

```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Admin: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)

## Backend applications

| App | Responsibility |
|-----|----------------|
| `accounts` | Users, roles, authentication foundation |
| `organisations` | Supply chain and regulator organisations |
| `products` | Medicine master data and batches |
| `serialization` | Serial numbers and QR identities |
| `inventory` | Stock levels and movements |
| `pharmacies` | Pharmacy profiles and licensing |
| `patients` | Patient profiles and medication search |
| `transactions` | Dispensing and prescription events |
| `verification` | Public verification events |
| `regulatory` | Regulator alerts and oversight |
| `audit` | Immutable audit trail foundation |
| `notifications` | Alerts and communications |
| `core` | Shared base models, constants, permissions |

## Technology direction

| Layer | Technology | Status |
|-------|------------|--------|
| Core backend | Django + DRF | Phase 1 |
| Database | PostgreSQL | Configured |
| Web | Next.js, TypeScript, Tailwind | Planned |
| Mobile | Flutter | Planned |
| High-speed services | FastAPI | Planned |
| AI | Python AI services | Planned |
| Blockchain | Hyperledger Fabric | Planned |

## Contributing and governance

This is government-grade infrastructure. Changes should follow documented architecture, security principles, and phased delivery in `docs/roadmap/`.

## Licence

To be defined by the programme authority.
