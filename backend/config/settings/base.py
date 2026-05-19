"""
NPTTE Django base settings.

Shared configuration for all environments. Environment-specific overrides
live in development.py and production.py.
"""
from datetime import timedelta
from pathlib import Path

import dj_database_url
import environ

BASE_DIR = Path(__file__).resolve().parent.parent.parent
APPS_DIR = BASE_DIR / "apps"

env = environ.Env(
    DEBUG=(bool, False),
    USE_SQLITE=(bool, False),
)

env_file = BASE_DIR / ".env"
if env_file.exists():
    environ.Env.read_env(env_file)

SECRET_KEY = env("SECRET_KEY", default="insecure-dev-key-change-before-deployment")
DEBUG = env("DEBUG")
ALLOWED_HOSTS = env.list("ALLOWED_HOSTS", default=["localhost", "127.0.0.1"])

CSRF_TRUSTED_ORIGINS = env.list("CSRF_TRUSTED_ORIGINS", default=[])
CORS_ALLOWED_ORIGINS = env.list("CORS_ALLOWED_ORIGINS", default=[])

INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "corsheaders",
    "rest_framework",
    "rest_framework_simplejwt",
    "rest_framework_simplejwt.token_blacklist",
    "drf_spectacular",
    "django_filters",
    # NPTTE domain applications
    "apps.core",
    "apps.accounts",
    "apps.organisations",
    "apps.products",
    "apps.serialization",
    "apps.inventory",
    "apps.pharmacies",
    "apps.patients",
    "apps.transactions",
    "apps.verification",
    "apps.regulatory",
    "apps.audit",
    "apps.notifications",
    # Phase 3 — national scale modules
    "apps.traceability",
    "apps.manufacturers",
    "apps.distributors",
    "apps.logistics",
    "apps.prescriptions",
    "apps.alerts",
    "apps.fraud_detection",
    "apps.compliance",
    "apps.geolocation",
    "apps.ai_engine",
    "apps.blockchain_bridge",
    "apps.analytics",
    "apps.national_dashboard",
    "apps.emergency",
    "apps.international",
    # Phase 5 — national command platform
    "apps.command_center",
    "apps.events",
    "apps.market_intelligence",
    "apps.citizen",
    "apps.onboarding",
    "apps.emergency_response",
    "apps.national_analytics",
    "apps.mobile",
    # Phase 6 — realtime operations (additive SSE)
    "apps.realtime",
    # Phase 10 — sovereign AI & operational intelligence (additive)
    "apps.certificates",
    "apps.developer_access",
    # Phase 11 — pilot readiness (additive)
    "apps.pilot_readiness",
    # Phase 12 — mobile scanning operations (additive)
    "apps.scanning",
    # Phase 13 — traceability demo walkthrough (additive, no models)
    "apps.traceability_demo",
    # Phase 14 — multi-tenant organisation infrastructure (additive)
    "apps.tenancy",
    # Phase 15 — operational persistence (additive)
    "apps.operations",
    # Phase 16 — external connectivity (additive)
    "apps.integrations",
    # Phase 17 — realtime event bus (additive)
    "apps.streambus",
    # Phase 18 — sovereign intelligence & enforcement (additive)
    "apps.intelligence",
    "apps.enforcement",
    # Phase 19 — drill-down intelligence explorer (additive)
    "apps.explorer",
    # Phase 20B preparation — copilot boundaries (no models, placeholders only)
    "apps.copilot",
    # Phase 20C — realtime command orchestration (additive)
    "apps.command_orchestration",
    # Phase 20A.2 — national operational demo seed (no models)
    "apps.operational_demo",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "corsheaders.middleware.CorsMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "apps.core.middleware.APIAuditMiddleware",
    "apps.tenancy.middleware.TenantContextMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "config.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / "templates"],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "config.wsgi.application"
ASGI_APPLICATION = "config.asgi.application"

AUTH_USER_MODEL = "accounts.User"

# Database: DATABASE_URL (Render) > PostgreSQL vars > SQLite fallback
if env("USE_SQLITE"):
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }
elif env.str("DATABASE_URL", default=""):
    DATABASES = {
        "default": dj_database_url.config(
            default=env("DATABASE_URL"),
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": env("DB_ENGINE", default="django.db.backends.postgresql"),
            "NAME": env("DB_NAME", default="nptte"),
            "USER": env("DB_USER", default="nptte"),
            "PASSWORD": env("DB_PASSWORD", default="nptte"),
            "HOST": env("DB_HOST", default="localhost"),
            "PORT": env("DB_PORT", default="5432"),
        }
    }

AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

LANGUAGE_CODE = "en-gb"
TIME_ZONE = "Africa/Lagos"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATIC_ROOT = BASE_DIR / "staticfiles"
STORAGES = {
    "default": {
        "BACKEND": "django.core.files.storage.FileSystemStorage",
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedManifestStaticFilesStorage",
    },
}
MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

# Phase 15 — email delivery (console locally; override via env in production)
EMAIL_BACKEND = env(
    "EMAIL_BACKEND",
    default="django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = env("DEFAULT_FROM_EMAIL", default="noreply@nptte.gov.ng")
NPTTE_FRONTEND_URL = env("NPTTE_FRONTEND_URL", default="http://localhost:3000")

# Phase 16 — integration providers (env-driven, no hardcoded vendors)
NPTTE_EMAIL_PROVIDER = env("NPTTE_EMAIL_PROVIDER", default="console")
NPTTE_SMS_PROVIDER = env("NPTTE_SMS_PROVIDER", default="mock")
NPTTE_STORAGE_BACKEND = env("NPTTE_STORAGE_BACKEND", default="local")
SENDGRID_API_KEY = env("SENDGRID_API_KEY", default="")
MAILGUN_API_KEY = env("MAILGUN_API_KEY", default="")
TWILIO_ACCOUNT_SID = env("TWILIO_ACCOUNT_SID", default="")
TWILIO_AUTH_TOKEN = env("TWILIO_AUTH_TOKEN", default="")
AFRICAS_TALKING_API_KEY = env("AFRICAS_TALKING_API_KEY", default="")
AWS_STORAGE_BUCKET_NAME = env("AWS_STORAGE_BUCKET_NAME", default="")
GCS_BUCKET_NAME = env("GCS_BUCKET_NAME", default="")
AZURE_STORAGE_CONNECTION_STRING = env("AZURE_STORAGE_CONNECTION_STRING", default="")

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# CORS — origins from environment; credentials for authenticated web clients
CORS_ALLOW_CREDENTIALS = True
CORS_ALLOWED_ORIGIN_REGEXES = env.list("CORS_ALLOWED_ORIGIN_REGEXES", default=[])
CORS_ALLOW_HEADERS = [
    "accept",
    "accept-encoding",
    "authorization",
    "content-type",
    "dnt",
    "origin",
    "user-agent",
    "x-csrftoken",
    "x-requested-with",
]

REST_FRAMEWORK = {
    "DEFAULT_AUTHENTICATION_CLASSES": [
        "rest_framework_simplejwt.authentication.JWTAuthentication",
        "rest_framework.authentication.SessionAuthentication",
    ],
    "DEFAULT_PERMISSION_CLASSES": [
        "rest_framework.permissions.IsAuthenticated",
    ],
    "DEFAULT_FILTER_BACKENDS": [
        "django_filters.rest_framework.DjangoFilterBackend",
        "rest_framework.filters.OrderingFilter",
        "rest_framework.filters.SearchFilter",
    ],
    "DEFAULT_PAGINATION_CLASS": "rest_framework.pagination.PageNumberPagination",
    "PAGE_SIZE": 25,
    "DEFAULT_SCHEMA_CLASS": "drf_spectacular.openapi.AutoSchema",
    "DEFAULT_THROTTLE_CLASSES": [
        "apps.core.throttling.NPTTEAnonThrottle",
        "apps.core.throttling.NPTTEUserThrottle",
    ],
    "DEFAULT_THROTTLE_RATES": {
        "anon": env("THROTTLE_ANON", default="200/hour"),
        "user": env("THROTTLE_USER", default="2000/hour"),
        "auth": env("THROTTLE_AUTH", default="30/minute"),
        "verify": env("THROTTLE_VERIFY", default="60/minute"),
        "citizen": env("THROTTLE_CITIZEN", default="30/minute"),
        "command": env("THROTTLE_COMMAND", default="500/hour"),
    },
}

# Async / cache hooks (Redis + Celery) — configure in production without code changes
REDIS_URL = env.str("REDIS_URL", default="")
CELERY_BROKER_URL = env.str("CELERY_BROKER_URL", default=REDIS_URL)
CELERY_RESULT_BACKEND = env.str("CELERY_RESULT_BACKEND", default=REDIS_URL)

# Django cache — Redis when REDIS_URL is set (Render); LocMem for local dev only
if REDIS_URL:
    CACHES = {
        "default": {
            "BACKEND": "django_redis.cache.RedisCache",
            "LOCATION": REDIS_URL,
            "OPTIONS": {
                "CLIENT_CLASS": "django_redis.client.DefaultClient",
                # Do not take down requests when Redis is briefly unavailable
                "IGNORE_EXCEPTIONS": True,
            },
            "KEY_PREFIX": "nptte",
        }
    }
else:
    CACHES = {
        "default": {
            "BACKEND": "django.core.cache.backends.locmem.LocMemCache",
            "LOCATION": "nptte-dev",
        }
    }

NPTTE_VERIFY_BASE_URL = env.str("NPTTE_VERIFY_BASE_URL", default="https://verify.nptte.gov.ng/v1")
NPTTE_VERIFICATION_HMAC_SECRET = env.str("NPTTE_VERIFICATION_HMAC_SECRET", default="")

SIMPLE_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(minutes=60),
    "REFRESH_TOKEN_LIFETIME": timedelta(days=7),
    "ROTATE_REFRESH_TOKENS": True,
    "BLACKLIST_AFTER_ROTATION": True,
    "UPDATE_LAST_LOGIN": True,
    "AUTH_HEADER_TYPES": ("Bearer",),
}

SPECTACULAR_SETTINGS = {
    "TITLE": "NPTTE API",
    "DESCRIPTION": (
        "National Pharmaceutical Transparency & Traceability Ecosystem — "
        "Nigeria pharmaceutical supply chain and patient medication discovery APIs."
    ),
    "VERSION": "5.0.0",
    "SERVE_INCLUDE_SCHEMA": False,
    "COMPONENT_SPLIT_REQUEST": True,
    "SCHEMA_PATH_PREFIX": r"/api/v1",
}
