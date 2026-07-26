"""
Django settings for config project.
"""

from pathlib import Path
from datetime import timedelta
import os
from urllib.parse import urlparse

import dj_database_url

BASE_DIR = Path(__file__).resolve().parent.parent



def env_bool(name, default=False):
    value = os.environ.get(name)
    if value is None:
        return default
    return value.strip().lower() in {'1', 'true', 'yes', 'on'}


def env_list(name, default=''):
    value = os.environ.get(name, default)
    return [item.strip() for item in value.split(',') if item.strip()]


def origin_host(value):
    """URL yoki host qiymatidan Django ALLOWED_HOSTS uchun host qaytaradi."""
    value = (value or '').strip()
    if not value:
        return ''
    parsed = urlparse(value if '://' in value else f'//{value}')
    return (parsed.hostname or value).strip()

SECRET_KEY = os.environ.get(
    'DJANGO_SECRET_KEY',
    'django-insecure-local-only-change-this-key',
)

DEBUG = env_bool('DJANGO_DEBUG', True)

# Railway domeni avtomatik qo'shiladi. Qo'shimcha domenlarni vergul bilan
# DJANGO_ALLOWED_HOSTS orqali kiriting.
ALLOWED_HOSTS = ['localhost', '127.0.0.1', '[::1]', '.railway.app']
ALLOWED_HOSTS += [origin_host(item) for item in env_list('DJANGO_ALLOWED_HOSTS')]
railway_public_domain = origin_host(os.environ.get('RAILWAY_PUBLIC_DOMAIN', ''))
if railway_public_domain:
    ALLOWED_HOSTS.append(railway_public_domain)
ALLOWED_HOSTS = list(dict.fromkeys(filter(None, ALLOWED_HOSTS)))


# Application definition

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',

    # 3rd party
    'rest_framework',
    'rest_framework_simplejwt',
    'corsheaders',

    # local apps
    'accounts',
    'courses',
    'exams',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'config.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'


# Database
# Lokal muhitda SQLite, Railway'da esa DATABASE_URL orqali PostgreSQL ishlaydi.
DATABASE_URL = os.environ.get('DATABASE_URL', '').strip()

if DATABASE_URL:
    DATABASES = {
        'default': dj_database_url.parse(
            DATABASE_URL,
            conn_max_age=600,
            conn_health_checks=True,
        )
    }
elif os.environ.get('DB_ENGINE') == 'postgresql':
    # Eski DB_* o'zgaruvchilari bilan ham ishlashda davom etadi.
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': os.environ.get('DB_NAME', 'talim_platformasi'),
            'USER': os.environ.get('DB_USER', 'postgres'),
            'PASSWORD': os.environ.get('DB_PASSWORD', ''),
            'HOST': os.environ.get('DB_HOST', 'localhost'),
            'PORT': os.environ.get('DB_PORT', '5432'),
            'CONN_MAX_AGE': 600,
            'CONN_HEALTH_CHECKS': True,
        }
    }
else:
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': os.environ.get('SQLITE_PATH', BASE_DIR / 'db.sqlite3'),
        }
    }


AUTH_USER_MODEL = 'accounts.User'


# Password validation

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]


# Internationalization

LANGUAGE_CODE = 'uz'
TIME_ZONE = 'Asia/Tashkent'
USE_I18N = True
USE_TZ = True


# Static & media files
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

# WhiteNoise Django admin va boshqa static fayllarni Railway'da xizmat qiladi.
STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    'staticfiles': {
        'BACKEND': 'whitenoise.storage.CompressedManifestStaticFilesStorage',
    },
}
WHITENOISE_MAX_AGE = 31536000 if not DEBUG else 0

MEDIA_URL = '/media/'
MEDIA_ROOT = Path(os.environ.get('MEDIA_ROOT', BASE_DIR / 'media'))
# Kichik loyihada media fayllarni Django orqali berish uchun. Railway Volume
# ulansa MEDIA_ROOT=/app/media qilib doimiy saqlash mumkin.
SERVE_MEDIA = env_bool('SERVE_MEDIA', True)


DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'


# ==================== REST FRAMEWORK ====================

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PERMISSION_CLASSES': (
        'rest_framework.permissions.IsAuthenticated',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 20,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(hours=8),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=7),
    'ROTATE_REFRESH_TOKENS': True,
    'AUTH_HEADER_TYPES': ('Bearer',),
}


# ==================== CORS / PRODUCTION URLS ====================

FRONTEND_PUBLIC_URL = os.environ.get('FRONTEND_PUBLIC_URL', 'http://localhost:5173').rstrip('/')

local_origins = [
    'http://localhost:3000',
    'http://localhost:5173',
    'http://localhost:5174',
    'http://localhost:5175',
    'http://127.0.0.1:3000',
    'http://127.0.0.1:5173',
    'http://127.0.0.1:5174',
    'http://127.0.0.1:5175',
]
CORS_ALLOWED_ORIGINS = local_origins + [item.rstrip('/') for item in env_list('CORS_ALLOWED_ORIGINS')]
if FRONTEND_PUBLIC_URL.startswith(('http://', 'https://')):
    CORS_ALLOWED_ORIGINS.append(FRONTEND_PUBLIC_URL)
CORS_ALLOWED_ORIGINS = list(dict.fromkeys(CORS_ALLOWED_ORIGINS))

# Netlify production va deploy-preview domenlari avtomatik ruxsat etiladi.
# Qo'shimcha regexlarni CORS_ALLOWED_ORIGIN_REGEXES orqali vergul bilan bering.
CORS_ALLOWED_ORIGIN_REGEXES = [r'^https://[a-zA-Z0-9-]+\.netlify\.app$']
CORS_ALLOWED_ORIGIN_REGEXES += env_list('CORS_ALLOWED_ORIGIN_REGEXES')
CORS_ALLOWED_ORIGIN_REGEXES = list(dict.fromkeys(CORS_ALLOWED_ORIGIN_REGEXES))
CORS_ALLOW_CREDENTIALS = True
if DEBUG:
    CORS_ALLOW_ALL_ORIGINS = True

CSRF_TRUSTED_ORIGINS = [item.rstrip('/') for item in env_list('CSRF_TRUSTED_ORIGINS')]
if FRONTEND_PUBLIC_URL.startswith(('http://', 'https://')):
    CSRF_TRUSTED_ORIGINS.append(FRONTEND_PUBLIC_URL)
if railway_public_domain:
    CSRF_TRUSTED_ORIGINS.append(f'https://{railway_public_domain}')
CSRF_TRUSTED_ORIGINS = list(dict.fromkeys(CSRF_TRUSTED_ORIGINS))

# Railway HTTPS reverse-proxy ortida to'g'ri ishlashi uchun.
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
USE_X_FORWARDED_HOST = True
SECURE_SSL_REDIRECT = env_bool('SECURE_SSL_REDIRECT', False)
SECURE_HSTS_SECONDS = int(os.environ.get('SECURE_HSTS_SECONDS', '0'))
SESSION_COOKIE_SECURE = not DEBUG
CSRF_COOKIE_SECURE = not DEBUG
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'

