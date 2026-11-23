"""Configuración del proyecto. Lo sensible se lee de .env (ver .env.example)."""
import sys
from pathlib import Path

import environ

BASE_DIR = Path(__file__).resolve().parent.parent
env = environ.Env(DEBUG=(bool, False))
environ.Env.read_env(BASE_DIR / '.env')

SECRET_KEY = env('SECRET_KEY', default='solo-para-pruebas-locales')
DEBUG = env('DEBUG')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS', default=['127.0.0.1', 'localhost'])
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS', default=[])

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'core',
    'users',
    'inicio',
    'negocios',
    'chat',
    'panel',
    'pagos',
    'canales',
    'crm',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'agente.urls'

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
                'core.context_processors.sitio',
            ],
        },
    },
]

WSGI_APPLICATION = 'agente.wsgi.application'

# MySQL si el .env trae DATABASE_NAME; si no, SQLite para probar rápido.
if env('DATABASE_NAME', default=''):
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.mysql',
            'NAME': env('DATABASE_NAME'),
            'USER': env('DATABASE_USER', default=''),
            'PASSWORD': env('DATABASE_PASSWORD', default=''),
            'HOST': env('DATABASE_HOST', default='127.0.0.1'),
            'PORT': env('DATABASE_PORT', default='3306'),
            'OPTIONS': {'charset': 'utf8mb4', 'init_command': "SET sql_mode='STRICT_TRANS_TABLES'"},
            'TEST': {'NAME': 'test_' + env('DATABASE_NAME'), 'CHARSET': 'utf8mb4', 'COLLATION': 'utf8mb4_0900_ai_ci'},
        }
    }
else:
    DATABASES = {'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': BASE_DIR / 'db.sqlite3'}}

AUTH_USER_MODEL = 'users.Usuario'
LOGIN_URL = 'users:entrar'
LOGIN_REDIRECT_URL = 'panel:inicio'
LOGOUT_REDIRECT_URL = 'users:entrar'

# Las contraseñas que vienen de la versión anterior están en bcrypt; al entrar se vuelven a guardar con PBKDF2.
PASSWORD_HASHERS = [
    'django.contrib.auth.hashers.PBKDF2PasswordHasher',
    'django.contrib.auth.hashers.BCryptPasswordHasher',
]
AUTH_PASSWORD_VALIDATORS = [
    {'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator', 'OPTIONS': {'min_length': 8}},
]

LANGUAGE_CODE = 'es-mx'
TIME_ZONE = 'America/Mexico_City'
USE_I18N = True
USE_TZ = True

STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'
MEDIA_URL = 'media/'
MEDIA_ROOT = BASE_DIR / 'media'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Dirección pública del sitio (para enlaces en avisos y en Stripe).
SITIO_URL = env('SITIO_URL', default='http://127.0.0.1:8000')

# Gemini (capa gratis): se prueban en orden; si uno está saturado, sigue el siguiente.
GEMINI_API_KEY = env('GEMINI_API_KEY', default='')
GEMINI_MODELOS = env.list('GEMINI_MODELOS', default=['gemini-3.5-flash', 'gemini-3.8-flash', 'gemini-flash-latest'])

# Stripe en modo de prueba.
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')
STRIPE_PRICE_ID = env('STRIPE_PRICE_ID', default='')
STRIPE_PORTAL_ID = env('STRIPE_PORTAL_ID', default='')

# WhatsApp Cloud API (Meta).
WHATSAPP_TOKEN = env('WHATSAPP_TOKEN', default='')
WHATSAPP_VERIFY_TOKEN = env('WHATSAPP_VERIFY_TOKEN', default='')
WHATSAPP_APP_SECRET = env('WHATSAPP_APP_SECRET', default='')
WHATSAPP_API_VERSION = env('WHATSAPP_API_VERSION', default='v23.0')
WHATSAPP_AVISOS_A_DUENO = env.bool('WHATSAPP_AVISOS_A_DUENO', default=True)

# CRM de Merkatics (sin dirección, los envíos quedan para descargar en CSV).
MERKATICS_CRM_URL = env('MERKATICS_CRM_URL', default='')
MERKATICS_CRM_TOKEN = env('MERKATICS_CRM_TOKEN', default='')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'consola': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['consola'], 'level': 'WARNING'},
}

# Las pruebas automáticas nunca llaman a servicios reales.
if len(sys.argv) > 1 and sys.argv[1] == 'test':
    GEMINI_API_KEY = STRIPE_SECRET_KEY = WHATSAPP_TOKEN = MERKATICS_CRM_URL = ''
