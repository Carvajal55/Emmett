from pathlib import Path
from pymongo import MongoClient
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# Quick-start development settings - unsuitable for production
# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('DJANGO_SECRET_KEY', 'django-insecure-m9ijd9dj+_p7yp+9b&a!2o!kkdl%06ap)$(!k-oq+y9gq_c)f3')

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = os.environ.get('DJANGO_DEBUG', 'True') == 'True'

ALLOWED_HOSTS = ["*"]

""" CSRF_TRUSTED_ORIGINS = [
    'https://*.safeware.cl', 
    'https://app.aurorachat.cl'
] """

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'django.contrib.humanize',
    'rest_framework',
    'core',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'corsheaders.middleware.CorsMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'main.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': ["templates"],
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

WSGI_APPLICATION = 'main.wsgi.application'
X_FRAME_OPTIONS = 'ALLOWALL'

# Database
# https://docs.djangoproject.com/en/4.1/ref/settings/#databases
# Database configuration
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'NAME': os.environ.get('MYSQL_DATABASE'),  # Primera base de datos
        'USER': os.environ.get('MYSQL_USER'),
        'PASSWORD': os.environ.get('MYSQL_PASSWORD'),
        'HOST': os.environ.get('MYSQL_HOST'),
        'PORT': os.environ.get('MYSQL_PORT', '3306'),
    }
}

# MongoDB Configuration
MONGO_DB = {
    "MONGOHOST": os.getenv('MONGOHOST', 'mongodb'),  # Este debería ser 'mongodb' para que coincida con docker-compose
    "MONGOUSER": os.getenv('MONGO_INITDB_ROOT_USERNAME', 'newMongoUser'),
    "MONGOPASS": os.getenv('MONGO_INITDB_ROOT_PASSWORD', 'newMongoPassword2024!'),
    "MONGO_DB_NAME": os.getenv('MONGO_DB_NAME', 'admin'),  # Base de datos para autenticación
    "MONGOPORT": 27017  # Puerto predeterminado de MongoDB
}
# Cadena de conexión

# Password validation
# https://docs.djangoproject.com/en/4.1/ref/settings/#auth-password-validators
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
# https://docs.djangoproject.com/en/4.1/topics/i18n/
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'UTC'
USE_I18N = True
USE_TZ = True

# Static files (CSS, JavaScript, Images)
# https://docs.djangoproject.com/en/4.1/howto/static-files/
STATIC_URL = 'static/'

STATICFILES_DIRS = [
    os.path.join(BASE_DIR, "static"),
]

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'mediafiles')

# Default primary key field type
# https://docs.djangoproject.com/en/4.1/ref/settings/#default-auto-field
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Email Configuration


# CORS Configuration
CORS_ALLOW_ALL_ORIGINS = True

# Celery Configuration
""" CELERY_BROKER_URL = "redis://redis:6379/0"
CELERY_RESULT_BACKEND = "redis://redis:6379/0"
CELERY_ACCEPT_CONTENT = ['application/json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE """


EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'mail.emmett.cl'  # El servidor SMTP
EMAIL_PORT = 465  # Puerto SMTP para SSL
EMAIL_USE_TLS = False  # No usar TLS
EMAIL_USE_SSL = True  # Activar SSL
EMAIL_HOST_USER = 'erp@emmett.cl'  # Tu correo en cPanel
EMAIL_HOST_PASSWORD = 'holahola4090'  # La contraseña de la cuenta de correo
DEFAULT_FROM_EMAIL = 'erp@emmett.cl'  # Dirección de correo que se usará como remitente

DATA_UPLOAD_MAX_MEMORY_SIZE = 104857600 
AUTHENTICATION_BACKENDS = ['django.contrib.auth.backends.ModelBackend']


