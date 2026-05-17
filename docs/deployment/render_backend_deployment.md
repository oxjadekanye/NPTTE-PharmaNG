# NPTTE Backend — Render Deployment Guide

Deploy the Django backend as a **Web Service** on [Render](https://render.com). This guide assumes Phase 1 architecture is unchanged: modular apps under `backend/apps/`, settings in `backend/config/`.

## Prerequisites

- Render account
- Git repository pushed to GitHub/GitLab (push only after you confirm)
- Domain name optional (Render provides `*.onrender.com`)

## 1. Create PostgreSQL on Render

1. In the Render dashboard, click **New +** → **PostgreSQL**.
2. Name the database (e.g. `nptte-postgres`).
3. Select region closest to your users (e.g. Frankfurt or Oregon).
4. Choose plan (Free tier acceptable for initial testing).
5. Click **Create Database**.
6. When ready, open the database → **Connections** → copy **Internal Database URL** (use internal URL from the backend service in the same region).

Example format:

```
postgres://nptte_user:xxxxxxxx@dpg-xxxxx-a/nptte_dbname
```

## 2. Create Web Service (backend)

| Setting | Value |
|---------|--------|
| **Service type** | Web Service |
| **Environment** | Python |
| **Root directory** | `backend` |
| **Branch** | `main` (or your default branch) |
| **Build command** | `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_roles && python manage.py seed_regulator_admin` |
| **Start command** | `gunicorn config.wsgi:application` |

### Python version

In Render → **Environment** → add:

| Key | Value |
|-----|--------|
| `PYTHON_VERSION` | `3.11.9` (or `3.12.x`) |

## 3. Required environment variables

Set these on the **Web Service** → **Environment**:

| Variable | Example / notes |
|----------|-----------------|
| `DJANGO_SETTINGS_MODULE` | `config.settings.production` |
| `SECRET_KEY` | Long random string (generate with `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`) |
| `DEBUG` | `False` |
| `USE_SQLITE` | `False` |
| `DATABASE_URL` | Paste **Internal Database URL** from Render PostgreSQL |
| `ALLOWED_HOSTS` | `nptte-backend.onrender.com` (your exact Render hostname, comma-separated if multiple) |
| `CSRF_TRUSTED_ORIGINS` | `https://nptte-backend.onrender.com` |
| `CORS_ALLOWED_ORIGINS` | Your canonical Vercel URL, e.g. `https://nptte-pharma-ng.vercel.app` (comma-separated if multiple) |
| `NPTTE_REGULATOR_PASSWORD` | **Required for frontend login** — creates/updates `nptte_admin` on each deploy (use a strong secret) |
| `NPTTE_REGULATOR_USERNAME` | Optional (default `nptte_admin`) |
| *(automatic)* | Production settings also allow all `https://*.vercel.app` preview deploy URLs via regex |

Optional hardening:

| Variable | Value |
|----------|--------|
| `SECURE_SSL_REDIRECT` | `True` (default in production settings) |
| `DATABASE_SSL_REQUIRE` | `False` (Render internal URLs often work without; set `True` if using external URL with SSL) |

### Connecting PostgreSQL to the web service

1. Create PostgreSQL first (step 1).
2. Create the Web Service (step 2).
3. In the Web Service → **Environment** → **Add Environment Variable**.
4. Key: `DATABASE_URL`
5. Value: copy from PostgreSQL → **Internal Database URL**.
6. Alternatively, use Render **Link Database** if offered — it injects `DATABASE_URL` automatically.

**Important:** Use the **internal** URL for the web service in the same region. Do not commit `DATABASE_URL` to git.

## 4. Deploy

1. Connect the Git repository to Render.
2. Set root directory to `backend`.
3. Save environment variables.
4. Click **Manual Deploy** or push to the linked branch.
5. Watch build logs for:
   - `pip install` success
   - `collectstatic` — static files copied to `staticfiles/`
   - `migrate` — all migrations applied

## 5. Post-deploy: create superuser

Render shell (Web Service → **Shell**):

```bash
python manage.py createsuperuser
```

Or one-off with env vars (Shell):

```bash
DJANGO_SUPERUSER_USERNAME=admin \
DJANGO_SUPERUSER_EMAIL=admin@nptte.gov.ng \
DJANGO_SUPERUSER_PASSWORD='your-secure-password' \
python manage.py createsuperuser --noinput
```

## 6. Verify deployment

1. Open `https://<your-service>.onrender.com/admin/`
2. Log in with the superuser account.
3. Confirm domain apps appear in admin (Organisations, Products, Patients, etc.).

## Phase 2 API notes

After deploying Phase 2, verify:

- `GET /api/v1/health/` returns `healthy`
- `GET /api/docs/` loads Swagger UI
- Run `python manage.py seed_roles` once via Shell (optional: `seed_demo_data` for staging only)
- Regulator command-center login (Render Shell):

```bash
NPTTE_REGULATOR_PASSWORD='your-secure-password' python manage.py seed_regulator_admin
```

Default local/staging user when `DEBUG=True` and password env is unset: `nptte_admin` / `NptteAdmin2026!` (role `NAFDAC_ADMIN`, superuser).
- Ensure `token_blacklist` migrations are applied (included in `migrate`)

No changes to build/start commands are required for Phase 2.

## 7. Build and start commands (reference)

**Build command:**

```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate && python manage.py seed_roles && python manage.py seed_regulator_admin
```

**Start command:**

```bash
gunicorn config.wsgi:application
```

WSGI path is `config.wsgi:application` because `manage.py` and `config/` live inside the `backend` root directory.

## 8. Troubleshooting

| Issue | Fix |
|-------|-----|
| `DisallowedHost` | Add Render hostname to `ALLOWED_HOSTS` |
| CSRF failure on admin login | Add `https://your-app.onrender.com` to `CSRF_TRUSTED_ORIGINS` |
| CORS blocked from Vercel | Set `CORS_ALLOWED_ORIGINS` to your Vercel URL; redeploy after pull (includes `*.vercel.app` regex) |
| Static files 404 | Ensure build runs `collectstatic`; WhiteNoise is enabled in settings |
| Database connection error | Verify `DATABASE_URL`, `USE_SQLITE=False`, PostgreSQL is running |
| `USE_SQLITE must be False in production` | Set `USE_SQLITE=False` and provide `DATABASE_URL` |
| Migration errors | Run `python manage.py migrate` in Shell; check logs |

## 9. Not in scope (Phase 1)

- Frontend (Next.js) deployment
- Flutter mobile apps
- AI engine or blockchain layer
- FastAPI microservices
- Custom domains with CDN (optional later)

See [production_checklist.md](./production_checklist.md) before go-live.
