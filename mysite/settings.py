"""
Django settings for mysite project.
"""

from pathlib import Path

import environ
import os

BASE_DIR = Path(__file__).resolve().parent.parent

SECRET_KEY = 'django-insecure-+seit+dk$0*euh%hqn=_7n@wqp5e=0g_8_=j#5bhpa!%ptfvup'

DEBUG = True

ALLOWED_HOSTS = ['127.0.0.1', 'localhost', 'biblprompt.ru', 'www.biblprompt.ru', 'ninjapromt.ru', 'www.ninjapromt.ru', 'ninjaprompt.ru', 'www.ninjaprompt.ru',  '89.111.154.203' ]

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
        'DIRS': [BASE_DIR / 'templates'],   # ← добавили эту строку
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

env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

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

AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator'},
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator'},
    {'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator'},
    {'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator'},
]

LANGUAGE_CODE = 'ru-ru'
TIME_ZONE = 'Europe/Moscow'
USE_I18N = True
USE_TZ = True

STATIC_URL = '/static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = [
    BASE_DIR / 'static',           # корневая папка static
]

MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Увеличиваем лимит загрузки файлов в Django до 300 МБ
DATA_UPLOAD_MAX_MEMORY_SIZE = 314572800    # 300 МБ
FILE_UPLOAD_MAX_MEMORY_SIZE = 314572800    # 300 МБ

# Дополнительно (рекомендуется)
DATA_UPLOAD_MAX_NUMBER_FILES = 100

# ====================== АВТОРИЗАЦИЯ ======================
LOGIN_URL = '/admin/login/'        # логин теперь только в админке
LOGIN_REDIRECT_URL = '/'           # после входа в админку — на главную
LOGOUT_REDIRECT_URL = '/'          # после выхода — на главную'

CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.locmem.LocMemCache',
    }
}

SILENCED_SYSTEM_CHECKS = ['django_ratelimit.E003', 'django_ratelimit.W001']

# CSRF настройки для максимальной совместимости
CSRF_COOKIE_NAME = 'csrftoken'
CSRF_COOKIE_HTTPONLY = False          # ← критично для JS
CSRF_COOKIE_SAMESITE = 'Lax'          # или 'None' если будешь HTTPS + Secure
CSRF_TRUSTED_ORIGINS = [
    'https://ninjaprompt.ru',
    'https://www.ninjaprompt.ru',
    'https://*.ninjaprompt.ru',
]

# Рекомендуется в production
SECURE_SSL_REDIRECT = True
SECURE_PROXY_SSL_HEADER = ('HTTP_X_FORWARDED_PROTO', 'https')
