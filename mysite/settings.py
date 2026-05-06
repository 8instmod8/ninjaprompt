"""
Django settings for ninjaprompt project.
Production-ready + hardened (2026)
"""

from pathlib import Path
import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent

env = environ.Env(
    DEBUG=(bool, False),
    SECRET_KEY=(str, None),
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

# === SECURITY (КРИТИЧНО) ===
SECRET_KEY = env('SECRET_KEY')          # ← только из .env
DEBUG = env.bool('DEBUG', default=False)

ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=[
    '127.0.0.1',
    'localhost',
])

# === APPLICATIONS ===
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django_ratelimit',
    'django_telegram_login',
    'content',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'mysite.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [BASE_DIR / 'templates'],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
            ],
        },
    },
]

WSGI_APPLICATION = 'mysite.wsgi.application'

# === DATABASE (только через .env) ===
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
    }
}

# === PASSWORD VALIDATORS ===
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

# === INTERNATIONALIZATION ===
LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

# === STATIC & MEDIA ===
STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
STATICFILES_DIRS = [BASE_DIR / 'static']

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

DATA_UPLOAD_MAX_MEMORY_SIZE = 314572800
FILE_UPLOAD_MAX_MEMORY_SIZE = 314572800

# === AUTH ===
LOGIN_URL = '/admin/login/'
LOGIN_REDIRECT_URL = '/'
LOGOUT_REDIRECT_URL = '/'

# === CSRF & SECURITY HEADERS ===
CSRF_COOKIE_HTTPONLY = env.bool('CSRF_COOKIE_HTTPONLY', default=False)
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[
    'https://ninjaprompt.ru',
    'https://www.ninjaprompt.ru',
])

SECURE_SSL_REDIRECT = env.bool('SECURE_SSL_REDIRECT', default=True)
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

SILENCED_SYSTEM_CHECKS = ['django_ratelimit.E003', 'django_ratelimit.W001']
