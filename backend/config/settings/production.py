"""
Production settings for Render and other hosted deployments.

Enable via: DJANGO_SETTINGS_MODULE=config.settings.production
"""
import dj_database_url

from .base import *  # noqa: F403

DEBUG = env.bool("DEBUG", default=False)  # noqa: F405

# Compress JSON API responses (SSE streams are not affected — no GZip on event-stream)
MIDDLEWARE = [  # noqa: F405
    "django.middleware.security.SecurityMiddleware",
    "django.middleware.gzip.GZipMiddleware",
    *MIDDLEWARE[1:],  # noqa: F405
]

# Require DATABASE_URL on Render; never use SQLite in production
if env("USE_SQLITE"):  # noqa: F405
    raise ValueError("USE_SQLITE must be False in production.")

if env.str("DATABASE_URL", default=""):  # noqa: F405
    DATABASES = {  # noqa: F811
        "default": dj_database_url.config(
            default=env("DATABASE_URL"),  # noqa: F405
            conn_max_age=600,
            conn_health_checks=True,
            ssl_require=env.bool("DATABASE_SSL_REQUIRE", default=False),  # noqa: F405
        )
    }
elif not env("USE_SQLITE"):  # noqa: F405
    # Individual DB_* vars from environment (fallback if DATABASE_URL not set)
    pass  # DATABASES already configured in base.py

# Security
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env.bool("SECURE_SSL_REDIRECT", default=True)  # noqa: F405
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True
SECURE_HSTS_SECONDS = env.int("SECURE_HSTS_SECONDS", default=31536000)  # noqa: F405
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_BROWSER_XSS_FILTER = True
X_FRAME_OPTIONS = "DENY"

# Trust Render / reverse proxy host headers
USE_X_FORWARDED_HOST = True

# CORS — allow Vercel production and preview deployments (additive to CORS_ALLOWED_ORIGINS)
_vercel_origin_regexes = [
    r"^https://[\w.-]+\.vercel\.app$",
]
CORS_ALLOWED_ORIGIN_REGEXES = list(  # noqa: F405
    dict.fromkeys(
        env.list("CORS_ALLOWED_ORIGIN_REGEXES", default=[]) + _vercel_origin_regexes  # noqa: F405
    )
)
