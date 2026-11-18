"""Configuración del backend de la Fase 2 (Django + MySQL).

Todo lo secreto o lo que cambia entre la compu de Arleth y PythonAnywhere se
lee de `backend/.env` (no se sube a git). Ver `.env.example`.
"""
import os
from pathlib import Path

import pymysql
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / '.env')

# PyMySQL hace de puente con MySQL sin compilar nada (funciona igual en la Mac
# y en PythonAnywhere).
pymysql.version_info = (2, 2, 7, 'final', 0)
pymysql.install_as_MySQLdb()


def entorno(nombre, defecto=''):
    return os.environ.get(nombre, defecto)


SECRET_KEY = entorno('DJANGO_SECRET_KEY') or 'solo-para-pruebas-locales'
DEBUG = entorno('DJANGO_DEBUG') == '1'
ALLOWED_HOSTS = [h.strip() for h in entorno('DJANGO_ALLOWED_HOSTS', '127.0.0.1,localhost').split(',') if h.strip()]

INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'rest_framework',
    'rest_framework.authtoken',
    'corsheaders',
    'negocios',
    'chat',
    'canales',
    'crm',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'corsheaders.middleware.CorsMiddleware',
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
            ],
        },
    },
]

WSGI_APPLICATION = 'agente.wsgi.application'

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': entorno('MYSQL_NAME', 'agente_pyme'),
        'USER': entorno('MYSQL_USER', 'agente'),
        'PASSWORD': entorno('MYSQL_PASSWORD'),
        'HOST': entorno('MYSQL_HOST', '127.0.0.1'),
        'PORT': entorno('MYSQL_PORT', '3306'),
        'OPTIONS': {
            'charset': 'utf8mb4',
            'init_command': "SET sql_mode='STRICT_TRANS_TABLES'",
        },
        'TEST': {'NAME': 'test_' + entorno('MYSQL_NAME', 'agente_pyme')},
    }
}

# Las contraseñas de la Fase 1 (Supabase) vienen en bcrypt: Django las acepta
# tal cual y, al entrar, las vuelve a guardar con su método principal.
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
STATIC_ROOT = BASE_DIR / 'static'
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': ['rest_framework.authentication.TokenAuthentication'],
    'DEFAULT_PERMISSION_CLASSES': ['rest_framework.permissions.IsAuthenticated'],
    'DEFAULT_THROTTLE_RATES': {'chat': '30/min', 'entrar': '10/min'},
}

# Las pantallas (Vite) pueden vivir en otro dominio mientras dura la mudanza.
CORS_ALLOWED_ORIGINS = [o.strip() for o in entorno('CORS_ORIGENES', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if o.strip()]

# Llaves de servicios externos (se llenan en sus tickets).
GEMINI_API_KEY = entorno('GEMINI_API_KEY')
STRIPE_SECRET_KEY = entorno('STRIPE_SECRET_KEY')
STRIPE_WEBHOOK_SECRET = entorno('STRIPE_WEBHOOK_SECRET')
STRIPE_PRICE_ID = entorno('STRIPE_PRICE_ID')
STRIPE_PORTAL_ID = entorno('STRIPE_PORTAL_ID')
WHATSAPP_TOKEN = entorno('WHATSAPP_TOKEN')
WHATSAPP_VERIFY_TOKEN = entorno('WHATSAPP_VERIFY_TOKEN')
WHATSAPP_APP_SECRET = entorno('WHATSAPP_APP_SECRET')

GEMINI_MODELO = entorno('GEMINI_MODELO', 'gemini-2.5-flash')
WHATSAPP_API_VERSION = entorno('WHATSAPP_API_VERSION', 'v23.0')
WHATSAPP_AVISOS_A_DUENO = entorno('WHATSAPP_AVISOS_A_DUENO') == '1'

# Dirección pública de las pantallas (para los enlaces de los avisos).
SITIO_URL = entorno('SITIO_URL', 'http://localhost:5173')

# F2-10 Avisos por correo (opcional). Gratis con una cuenta de Gmail y una
# «contraseña de aplicación». Sin EMAIL_HOST no se manda correo.
EMAIL_HOST = entorno('EMAIL_HOST')
EMAIL_PORT = int(entorno('EMAIL_PORT', '587'))
EMAIL_HOST_USER = entorno('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = entorno('EMAIL_HOST_PASSWORD')
EMAIL_USE_TLS = True
DEFAULT_FROM_EMAIL = entorno('EMAIL_DE', EMAIL_HOST_USER or 'avisos@localhost')

# F2-11 CRM de Merkatics (cuando den su dirección; sin ella, los envíos quedan para CSV).
MERKATICS_CRM_URL = entorno('MERKATICS_CRM_URL')
MERKATICS_CRM_TOKEN = entorno('MERKATICS_CRM_TOKEN')

LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {'consola': {'class': 'logging.StreamHandler'}},
    'root': {'handlers': ['consola'], 'level': 'WARNING'},
}
