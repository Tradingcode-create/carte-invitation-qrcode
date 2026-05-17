from pathlib import Path
import os
try:
    import dj_database_url
except ImportError:  # pragma: no cover - fallback local
    dj_database_url = None


BASE_DIR = Path(__file__).resolve().parent.parent


def env_bool(name, default=False):
    return os.environ.get(name, str(default)).strip().lower() in {"1", "true", "yes", "on"}


def env_list(name, default=""):
    raw_value = os.environ.get(name, default)
    return [item.strip() for item in raw_value.split(",") if item.strip()]

SECRET_KEY = "django-insecure-change-me-before-production"
DEBUG = env_bool("DEBUG", default=True)
ALLOWED_HOSTS = [
    ".onrender.com",
    "localhost",
    "127.0.0.1",
]
ALLOWED_HOSTS += env_list("ALLOWED_HOSTS")

CSRF_TRUSTED_ORIGINS = [
    "https://carte-invitation-qrcode.onrender.com",
]
CSRF_TRUSTED_ORIGINS += env_list("CSRF_TRUSTED_ORIGINS")


INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "invitations",
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "whitenoise.middleware.WhiteNoiseMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.locale.LocaleMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
    "invitations.middleware.SessionActivityMiddleware",
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


if dj_database_url:
    DATABASES = {
        "default": dj_database_url.config(
            default=f"sqlite:///{BASE_DIR / 'db.sqlite3'}",
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
else:
    DATABASES = {
        "default": {
            "ENGINE": "django.db.backends.sqlite3",
            "NAME": BASE_DIR / "db.sqlite3",
        }
    }

SESSION_ENGINE = "django.contrib.sessions.backends.db"
SESSION_COOKIE_AGE = 60 * 30
SESSION_IDLE_TIMEOUT = 60 * 30
SESSION_SAVE_EVERY_REQUEST = False
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_PROXY_SSL_HEADER = ("HTTP_X_FORWARDED_PROTO", "https")
SECURE_SSL_REDIRECT = env_bool("SECURE_SSL_REDIRECT", default=not DEBUG)


AUTH_PASSWORD_VALIDATORS = []

LANGUAGE_CODE = "fr-fr"
LANGUAGES = [
    ("fr", "Francais"),
    ("en", "English"),
]
TIME_ZONE = "Europe/Paris"
USE_I18N = True
USE_TZ = True

STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]
STATIC_ROOT = BASE_DIR / "staticfiles"

MEDIA_URL = "media/"
MEDIA_ROOT = BASE_DIR / "media"

LOGIN_REDIRECT_URL = "invitations:home"
LOGOUT_REDIRECT_URL = "invitations:home"
LOGIN_URL = "login"

EMAIL_BACKEND = os.environ.get(
    "DJANGO_EMAIL_BACKEND",
    "django.core.mail.backends.console.EmailBackend",
)
DEFAULT_FROM_EMAIL = os.environ.get("DEFAULT_FROM_EMAIL", "no-reply@invitationstudio.local")
ADMIN_CONTACT_EMAIL = os.environ.get("ADMIN_CONTACT_EMAIL", DEFAULT_FROM_EMAIL)

DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"
STATICFILES_STORAGE = "whitenoise.storage.CompressedManifestStaticFilesStorage"
