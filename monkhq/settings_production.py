import os
from pathlib import Path

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = False

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = os.environ.get('SECRET_KEY', 'django-insecure-change-this-in-production-replace-with-secure-key')

# Allowed hosts for Koyeb
ALLOWED_HOSTS = [
    'localhost',
    '127.0.0.1',
    os.environ.get('KOYEB_APP_NAME', '').replace('-', '.') + '.koyeb.app',
    'monkhq.com',
    'www.monkhq.com',
    '*.koyeb.app'
]

# Application definition
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'core',
]

MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

ROOT_URLCONF = 'monkhq.urls'

TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [],
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

WSGI_APPLICATION = 'monkhq.wsgi.application'

# Database configuration for production with Neon PostgreSQL
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://monkhq_user:monkhq_password@localhost:5432/monkhq")

# For Neon, we need to manually parse the DATABASE_URL due to complex hostname
if 'ep-tiny-field-an0w3uqj-pooler.c-6.us-east-1.aws.neon.tech' in DATABASE_URL:
    # Extract components manually for Neon
    import re
    
    # Parse DATABASE_URL manually with exact hostname extraction
    pattern = r'postgresql://([^:]+):([^@]+)@([^:/]+):?(\d+)?/([^?]+)'
    match = re.match(pattern, DATABASE_URL)
    
    if match:
        user, password, hostname, port, database = match.groups()
        
        # Ensure we have the complete hostname
        full_hostname = 'ep-tiny-field-an0w3uqj-pooler.c-6.us-east-1.aws.neon.tech'
        
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': database,
                'USER': user,
                'PASSWORD': password,
                'HOST': full_hostname,  # Use the complete hostname
                'PORT': int(port) if port else 5432,
                'OPTIONS': {
                    'sslmode': 'require',
                    'channel_binding': 'require',
                },
                'CONN_MAX_AGE': 600,  # Persistent connections
            }
        }
    else:
        # Fallback to standard parsing
        from urllib.parse import urlparse, parse_qsl
        tmpPostgres = urlparse(DATABASE_URL)
        DATABASES = {
            'default': {
                'ENGINE': 'django.db.backends.postgresql',
                'NAME': tmpPostgres.path.replace('/', ''),
                'USER': tmpPostgres.username,
                'PASSWORD': tmpPostgres.password,
                'HOST': tmpPostgres.hostname,
                'PORT': tmpPostgres.port or 5432,
                'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
                'CONN_MAX_AGE': 600,
            }
        }
else:
    # Fallback database configuration
    from urllib.parse import urlparse, parse_qsl
    tmpPostgres = urlparse(DATABASE_URL)
    DATABASES = {
        'default': {
            'ENGINE': 'django.db.backends.postgresql',
            'NAME': tmpPostgres.path.replace('/', ''),
            'USER': tmpPostgres.username,
            'PASSWORD': tmpPostgres.password,
            'HOST': tmpPostgres.hostname,
            'PORT': tmpPostgres.port or 5432,
            'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
            'CONN_MAX_AGE': 600,
        }
    }

# Static files configuration
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATIC_URL = '/static/'

# Media files configuration
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')
MEDIA_URL = '/media/'

# Security settings
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Session security
SESSION_COOKIE_SECURE = True
SESSION_COOKIE_HTTPONLY = True
SESSION_COOKIE_SAMESITE = 'Strict'
CSRF_COOKIE_SECURE = True
CSRF_COOKIE_HTTPONLY = True
CSRF_COOKIE_SAMESITE = 'Strict'

# SSL redirect (only in production)
SECURE_SSL_REDIRECT = True

# Email configuration for Koyeb
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = os.environ.get('EMAIL_HOST', 'smtp.gmail.com')
EMAIL_PORT = os.environ.get('EMAIL_PORT', 587)
EMAIL_USE_TLS = os.environ.get('EMAIL_USE_TLS', 'True').lower() == 'true'
EMAIL_HOST_USER = os.environ.get('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = os.environ.get('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = os.environ.get('DEFAULT_FROM_EMAIL', 'hello@monkhq.com')

# Cache configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://redis:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        },
        'KEY_PREFIX': 'monkhq_',
        'TIMEOUT': 300,
    }
}

# Session configuration with Redis
SESSION_ENGINE = 'django.contrib.sessions.backends.cache'
SESSION_CACHE_ALIAS = 'default'

# Logging configuration for Koyeb
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
        'simple': {
            'format': '{levelname} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
    },
    'root': {
        'handlers': ['console'],
        'level': 'INFO',
    },
    'loggers': {
        'django': {
            'handlers': ['console'],
            'level': 'INFO',
            'propagate': False,
        },
        'monkhq': {
            'handlers': ['console'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}

# Performance optimizations for Koyeb
CONN_MAX_AGE = 600
TEMPLATES[0]['OPTIONS']['loaders'] = [
    ('django.template.loaders.cached.Loader', [
        'django.template.loaders.filesystem.Loader',
        'django.template.loaders.app_directories.Loader',
    ]),
]

# Middleware optimizations for Koyeb
MIDDLEWARE = [
    'whitenoise.middleware.WhiteNoiseMiddleware',
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
]

# WhiteNoise configuration for static files
WHITENOISE_USE_FINDERS = True
WHITENOISE_MAX_AGE = 31536000  # 1 year for static files
WHITENOICE_IGNORE_FILES = r'(?i)(\.DS_Store|\.git|\.hg|\.bzr|\.svn|__pycache__|node_modules)$'

# Koyeb-specific optimizations
USE_TZ = True
TIME_ZONE = 'UTC'

# Health check endpoint
def health_check(request):
    from django.http import JsonResponse
    from django.db import connection
    try:
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception:
        db_status = "unhealthy"
    
    return JsonResponse({
        'status': 'healthy',
        'database': db_status,
        'version': '1.0.0'
    })
