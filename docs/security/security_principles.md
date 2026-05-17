# Security Principles

NPTTE handles medicine traceability and citizen health data. Security is mandatory, not optional.

## 1. Defence in depth

- Network segmentation (DMZ, app tier, database tier)
- WAF and DDoS protection at edge
- Principle of least privilege for all service accounts
- Separate secrets per environment (dev/staging/production)

## 2. Identity and access

- Custom `accounts.User` with role-based access control (RBAC)
- Regulator actions require elevated roles and full audit logging
- Organisation-scoped data access for supply chain users
- Multi-factor authentication for admin and regulator accounts (planned)
- Account lockout and suspicious login detection (planned)

## 3. Data protection

- TLS 1.2+ for all external traffic
- Encryption at rest for PostgreSQL and object storage
- Minimise PII collection; require explicit consent for location-based patient search
- `PatientProfile.consent_to_location_search` must be enforced before processing searches
- Prescription files stored in dedicated secure object storage with signed URLs

## 4. Audit and non-repudiation

- `audit.AuditLog` records actor, action, entity, and before/after snapshots
- Admin audit logs are read-only in Django admin
- Future: append-only DB policies and Hyperledger anchoring for tamper evidence

## 5. Application security

- Django ORM only (no raw SQL without review)
- CSRF protection for session-based flows
- Parameterised queries, XSS escaping via templates
- Security headers: HSTS, `X-Frame-Options`, `Content-Security-Policy` (production)
- Dependency scanning in CI (planned)
- Regular penetration testing aligned to government standards

## 6. API security

- JWT short-lived access tokens; refresh rotation
- Scope API keys to organisation and operation type
- Rate limiting on public verification and patient search
- Input validation via DRF serializers
- No sensitive data in URLs or logs

## 7. Serialization and anti-counterfeiting

- Serial numbers and QR payloads treated as security assets
- Verification events logged with IP and channel for fraud analytics
- Compromised serial ranges can be revoked via status flags (future workflow)

## 8. Operational security

- Centralised logging and SIEM integration (planned)
- Incident response playbooks for data breach and counterfeit surges
- Backups encrypted; restore tested quarterly
- Production settings: `DEBUG=False`, strong `SECRET_KEY`, `ALLOWED_HOSTS` restricted

## 9. Compliance alignment

Design aligns with expectations for:

- Nigeria Data Protection Act (NDPA) — lawful basis and consent for patient data
- NAFDAC regulatory reporting requirements
- National cyber security frameworks for government systems

## Phase 1 security posture

| Control | Status |
|---------|--------|
| Custom user model | Implemented |
| Environment-based secrets | `.env` pattern |
| Production hardening settings | Template in `production.py` |
| Audit log model | Implemented |
| API authentication | Not implemented |
| MFA | Not implemented |
| Field encryption | Not implemented |
