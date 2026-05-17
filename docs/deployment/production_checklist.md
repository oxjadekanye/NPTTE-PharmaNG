# NPTTE Production Deployment Checklist

Use this checklist before and after deploying the Phase 1 Django backend to Render (or any production host).

## Security and configuration

- [ ] **SECRET_KEY** has been changed from any development or example value. Generate a new unique key for production.
- [ ] **DEBUG** is set to `False` in production environment variables.
- [ ] **USE_SQLITE** is set to `False` in production.
- [ ] **PostgreSQL** is used online via `DATABASE_URL` (Render PostgreSQL or equivalent). SQLite must not be used in production.
- [ ] **ALLOWED_HOSTS** includes the exact Render backend hostname (e.g. `nptte-backend.onrender.com`). Add custom domains when configured.
- [ ] **CSRF_TRUSTED_ORIGINS** includes the full HTTPS backend URL (e.g. `https://nptte-backend.onrender.com`).
- [ ] **CORS_ALLOWED_ORIGINS** lists only trusted frontend origins (when web clients exist). Do not use `*` in production.
- [ ] **DJANGO_SETTINGS_MODULE** is `config.settings.production`.
- [ ] Database credentials and `SECRET_KEY` are stored only in the host environment, never in git.

## Build and runtime

- [ ] **Static files** — build runs `python manage.py collectstatic --noinput` without errors.
- [ ] **Migrations** — build or release step runs `python manage.py migrate` successfully against production PostgreSQL.
- [ ] **Gunicorn** start command is `gunicorn config.wsgi:application` with root directory `backend`.
- [ ] **Python version** on Render is 3.10+ (3.11+ recommended).
- [ ] Health check: service shows **Live** in Render dashboard after deploy.

## Access and smoke tests

- [ ] **Superuser** created after first deployment (`createsuperuser` via Render Shell).
- [ ] **Admin URL** tested: `https://<your-backend>/admin/` loads login page over HTTPS.
- [ ] Admin login succeeds with superuser credentials.
- [ ] Sample read in admin: Organisation types, Products, or Patients visible without errors.

## Explicitly out of scope (Phase 1)

- [ ] Confirm **no AI engine** deployment in this release.
- [ ] Confirm **no blockchain layer** deployment in this release.
- [ ] Confirm **no Flutter mobile** deployment in this release.
- [ ] Confirm **no Next.js frontend** deployment in this release (backend-only phase).
- [ ] Confirm **no public API endpoints** exposed beyond admin unless intentionally added in a later phase.

## Post go-live

- [ ] Rotate any credentials that were used in staging.
- [ ] Document superuser recovery procedure for operations team.
- [ ] Enable Render (or provider) database backups.
- [ ] Plan Phase 2: DRF APIs, patient medication search endpoint, organisation membership.

## Sign-off

| Role | Name | Date |
|------|------|------|
| Technical lead | | |
| Security review | | |
| Programme owner | | |
