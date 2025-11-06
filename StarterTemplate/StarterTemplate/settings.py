"""
Django settings for StarterTemplate project.
"""

from pathlib import Path
import os
from dotenv import load_dotenv
from mongoengine import connect

# Load environment variables
load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# -------------------------------------------------------------------
# MongoDB connection
# -------------------------------------------------------------------
MONGO_URI = os.getenv('MONGO_URI', 'mongodb://localhost:27017/testdb')
connect(host=MONGO_URI)

# -------------------------------------------------------------------
# SECURITY SETTINGS
# -------------------------------------------------------------------
SECRET_KEY = os.getenv("DJANGO_SECRET_KEY", "django-insecure-dev-key")
SECRET_KEY_FALLBACKS = []  # For session validation during key rotation
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ALLOWED_HOSTS = os.getenv("ALLOWED_HOSTS", "").split(",") if os.getenv("ALLOWED_HOSTS") else ["*"]

# -------------------------------------------------------------------
# APPLICATION DEFINITION
# -------------------------------------------------------------------
INSTALLED_APPS = [
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
    "mongoengine",
    "accounts", 
    "channels",
    "chat"
]

MIDDLEWARE = [
    "django.middleware.security.SecurityMiddleware",
    "django.contrib.sessions.middleware.SessionMiddleware",
    "django.middleware.common.CommonMiddleware",
    "django.middleware.csrf.CsrfViewMiddleware",
    "django.contrib.auth.middleware.AuthenticationMiddleware",
    "accounts.middleware.MongoEngineUserMiddleware",
    "django.contrib.messages.middleware.MessageMiddleware",
    "django.middleware.clickjacking.XFrameOptionsMiddleware",
]

ROOT_URLCONF = "StarterTemplate.urls"

TEMPLATES = [
    {
        "BACKEND": "django.template.backends.django.DjangoTemplates",
        "DIRS": [BASE_DIR / 'templates'],
        "APP_DIRS": True,
        "OPTIONS": {
            "context_processors": [
                "django.template.context_processors.debug",
                "django.template.context_processors.request",
                "django.contrib.auth.context_processors.auth",
                "django.contrib.messages.context_processors.messages",
            ],
        },
    },
]

WSGI_APPLICATION = "StarterTemplate.wsgi.application"
ASGI_APPLICATION = "StarterTemplate.asgi.application"

# -------------------------------------------------------------------
# CHANNELS CONFIGURATION (WebSocket support)
# -------------------------------------------------------------------
# Use Redis if REDIS_URL is set (Docker/Production), otherwise use InMemory (Development)
REDIS_URL = os.getenv("REDIS_URL", None)

if REDIS_URL:
    # Production/Docker: Use Redis for channel layers
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels_redis.core.RedisChannelLayer",
            "CONFIG": {
                "hosts": [REDIS_URL],
            },
        },
    }
else:
    # Development: Use in-memory channel layer
    CHANNEL_LAYERS = {
        "default": {
            "BACKEND": "channels.layers.InMemoryChannelLayer"
        }
    }

# -------------------------------------------------------------------
# DATABASES — Used only for Django sessions (MongoEngine handles User data)
# -------------------------------------------------------------------
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.sqlite3",
        "NAME": BASE_DIR / "db.sqlite3",
    }
}
# -------------------------------------------------------------------
# PASSWORD VALIDATION
# -------------------------------------------------------------------
AUTH_PASSWORD_VALIDATORS = [
    {"NAME": "django.contrib.auth.password_validation.UserAttributeSimilarityValidator"},
    {"NAME": "django.contrib.auth.password_validation.MinimumLengthValidator"},
    {"NAME": "django.contrib.auth.password_validation.CommonPasswordValidator"},
    {"NAME": "django.contrib.auth.password_validation.NumericPasswordValidator"},
]

# -------------------------------------------------------------------
# INTERNATIONALIZATION
# -------------------------------------------------------------------
LANGUAGE_CODE = "en-us"
TIME_ZONE = "UTC"
USE_I18N = True
USE_TZ = True

# -------------------------------------------------------------------
# STATIC FILES
# -------------------------------------------------------------------
STATIC_URL = "static/"
STATICFILES_DIRS = [BASE_DIR / "static"]

# -------------------------------------------------------------------
# AUTHENTICATION
# -------------------------------------------------------------------
AUTHENTICATION_BACKENDS = [
    'accounts.auth_backend.MongoEngineBackend',
]

# Django sessions with custom serializer for MongoEngine
SESSION_ENGINE = 'django.contrib.sessions.backends.db'
SESSION_SERIALIZER = 'StarterTemplate.session_serializer.MongoEngineSessionSerializer'

# -------------------------------------------------------------------
# LOGIN/LOGOUT REDIRECTS
# -------------------------------------------------------------------
LOGIN_REDIRECT_URL = 'profile'
LOGIN_URL = 'login'
LOGOUT_REDIRECT_URL = 'login'

# -------------------------------------------------------------------
# DEFAULT FIELD TYPE
# -------------------------------------------------------------------
DEFAULT_AUTO_FIELD = "django.db.models.BigAutoField"

# -------------------------------------------------------------------
# EMAIL CONFIGURATION
# -------------------------------------------------------------------
# Email backend - use console for development, SMTP for production
EMAIL_BACKEND = os.getenv(
    'EMAIL_BACKEND',
    'django.core.mail.backends.smtp.EmailBackend'  # Default to console for testing
)

# SMTP Configuration (for production)
EMAIL_HOST = os.getenv('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = int(os.getenv('EMAIL_PORT', '587'))
EMAIL_USE_TLS = os.getenv('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.getenv('EMAIL_USER', '')
EMAIL_HOST_PASSWORD = os.getenv('EMAIL_PASS', '')
DEFAULT_FROM_EMAIL = os.getenv('DEFAULT_FROM_EMAIL', 'noreply@startertemplate.com')

# Email timeout
EMAIL_TIMEOUT = 30

# -------------------------------------------------------------------
# ENCRYPTION CONFIGURATION (for chat messages)
# -------------------------------------------------------------------
ENCRYPTION_KEY = os.getenv('ENCRYPTION_KEY', 'your_default_encryption_key_change_this_in_production')

# -------------------------------------------------------------------
# GOOGLE OAUTH CONFIGURATION
# -------------------------------------------------------------------
# Get credentials from Google Cloud Console: https://console.cloud.google.com/
# Create OAuth 2.0 Client ID and set authorized redirect URIs:
#   Development: http://127.0.0.1:8000/auth/google/callback/
#   Docker/HTTPS: https://localhost/auth/google/callback/
#   Production:   https://yourdomain.com/auth/google/callback/
GOOGLE_OAUTH_CLIENT_ID = os.getenv('GOOGLE_OAUTH_CLIENT_ID', '')
GOOGLE_OAUTH_CLIENT_SECRET = os.getenv('GOOGLE_OAUTH_CLIENT_SECRET', '')

# -------------------------------------------------------------------
# SECURITY SETTINGS (HTTPS/Docker)
# -------------------------------------------------------------------
# Enable these in production with HTTPS
USE_X_FORWARDED_HOST = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')

# HTTPS/SSL Settings (for production)
if not DEBUG:
    CSRF_COOKIE_SECURE = True
    SESSION_COOKIE_SECURE = True
    SECURE_SSL_REDIRECT = False  # Nginx handles redirect
    SECURE_HSTS_SECONDS = 31536000
    SECURE_HSTS_INCLUDE_SUBDOMAINS = True
    SECURE_HSTS_PRELOAD = True
    SECURE_CONTENT_TYPE_NOSNIFF = True
    SECURE_BROWSER_XSS_FILTER = True
    X_FRAME_OPTIONS = 'SAMEORIGIN'

# CSRF Trusted Origins (for Docker/Nginx)
CSRF_TRUSTED_ORIGINS = [
    'https://localhost',
    'https://127.0.0.1',
]
# Add your production domain to CSRF_TRUSTED_ORIGINS
if os.getenv('PRODUCTION_DOMAIN'):
    CSRF_TRUSTED_ORIGINS.append(f"https://{os.getenv('PRODUCTION_DOMAIN')}")
