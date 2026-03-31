# MonkHQ Koyeb Deployment Guide

## Prerequisites

1. **Koyeb Account**: Sign up at [koyeb.com](https://koyeb.com)
2. **GitHub Repository**: Push your code to GitHub
3. **Environment Variables**: Configure required environment variables

## Quick Deployment

### Option 1: Using Koyeb CLI

```bash
# Install Koyeb CLI
curl -sL https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-linux-amd64 -o koyeb
chmod +x koyeb
sudo mv koyeb /usr/local/bin/

# Authenticate
koyeb auth login

# Deploy
koyeb app create monkhq --dockerfile Dockerfile --port 8000
```

### Option 2: Using Koyeb Dashboard

1. Go to [Koyeb Dashboard](https://app.koyeb.com)
2. Click "Create App"
3. Connect your GitHub repository
4. Select the repository containing MonkHQ
5. Configure deployment settings

## Environment Variables

Set these environment variables in Koyeb:

```bash
# Django Settings
DJANGO_SETTINGS_MODULE=monkhq.settings_production
SECRET_KEY=your-very-secret-key-here
DEBUG=False
ALLOWED_HOSTS=*.koyeb.app,monkhq.com,www.monkhq.com

# Database (if using PostgreSQL)
DB_HOST=your-db-host
DB_PORT=5432
DB_NAME=monkhq
DB_USER=postgres
DB_PASSWORD=your-db-password

# Email Configuration
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=your-sendgrid-username
EMAIL_HOST_PASSWORD=your-sendgrid-password
DEFAULT_FROM_EMAIL=hello@monkhq.com

# Redis (if using)
REDIS_URL=redis://your-redis-host:6379/1

# Optional: Create superuser
DJANGO_CREATE_SUPERUSER=True
DJANGO_SUPERUSER_USERNAME=admin
DJANGO_SUPERUSER_EMAIL=admin@monkhq.com
DJANGO_SUPERUSER_PASSWORD=your-admin-password
```

## Performance Optimizations

### 1. Database Optimization

```python
# Add to settings_production.py
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME'),
        'USER': os.environ.get('DB_USER'),
        'PASSWORD': os.environ.get('DB_PASSWORD'),
        'HOST': os.environ.get('DB_HOST'),
        'PORT': os.environ.get('DB_PORT'),
        'OPTIONS': {
            'MAX_CONNS': 20,
            'CONN_MAX_AGE': 600,
        }
    }
}
```

### 2. Static File Optimization

```python
# Add to settings_production.py
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### 3. Caching Strategy

```python
# Add to settings_production.py
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Cache middleware
MIDDLEWARE = [
    'django.middleware.cache.UpdateCacheMiddleware',
    'django.middleware.common.CommonMiddleware',
    'django.middleware.cache.FetchFromCacheMiddleware',
    # ... other middleware
]

CACHE_MIDDLEWARE_ALIAS = 'default'
CACHE_MIDDLEWARE_SECONDS = 600
CACHE_MIDDLEWARE_KEY_PREFIX = ''
```

## Monitoring and Logging

### 1. Application Metrics

Add monitoring to your views:

```python
import time
from django.http import JsonResponse

def monitor_performance(view_func):
    def wrapper(request, *args, **kwargs):
        start_time = time.time()
        response = view_func(request, *args, **kwargs)
        end_time = time.time()
        
        # Log performance metrics
        print(f"View {view_func.__name__} took {end_time - start_time:.2f}s")
        
        return response
    return wrapper
```

### 2. Error Tracking with Sentry

```python
# Add to settings_production.py
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration

sentry_sdk.init(
    dsn="your-sentry-dsn",
    integrations=[DjangoIntegration()],
    traces_sample_rate=1.0,
    send_default_pii=True
)
```

## Scaling Configuration

### Horizontal Scaling

In your `koyeb.yaml`:

```yaml
scaling:
  min: 1
  max: 5
  target_cpu_percent: 70
  target_memory_percent: 80
```

### Database Scaling

1. **Read Replicas**: Configure read replicas for better performance
2. **Connection Pooling**: Use PgBouncer for connection pooling
3. **Indexing**: Add database indexes for frequently queried fields

## Security Best Practices

### 1. HTTPS and SSL

```python
# Add to settings_production.py
SECURE_SSL_REDIRECT = True
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True
```

### 2. Environment Security

- Use Koyeb's encrypted environment variables
- Rotate secrets regularly
- Use strong, unique passwords

### 3. Application Security

```python
# Add to settings_production.py
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
X_FRAME_OPTIONS = 'DENY'
```

## Backup Strategy

### 1. Database Backups

```bash
# Add to your Dockerfile or startup script
#!/bin/bash
# Backup script
pg_dump $DATABASE_URL > backup_$(date +%Y%m%d_%H%M%S).sql
```

### 2. Media File Backups

```python
# Use AWS S3 or similar for media storage
DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
AWS_ACCESS_KEY_ID = os.environ.get('AWS_ACCESS_KEY_ID')
AWS_SECRET_ACCESS_KEY = os.environ.get('AWS_SECRET_ACCESS_KEY')
AWS_STORAGE_BUCKET_NAME = 'monkhq-media'
```

## Troubleshooting

### Common Issues

1. **Database Connection Errors**
   - Check environment variables
   - Verify database is accessible from Koyeb

2. **Static File 404s**
   - Run `collectstatic` during deployment
   - Check STATIC_ROOT configuration

3. **Memory Issues**
   - Reduce Gunicorn workers
   - Enable database connection pooling

### Health Checks

Monitor your app health at:
- `/health/` - Basic health check
- `/ready/` - Readiness check
- `/alive/` - Liveness check

## Cost Optimization

1. **Right-size Instances**: Start with nano instances and scale up
2. **Database Optimization**: Use connection pooling
3. **CDN for Static Files**: Use Koyeb's built-in CDN
4. **Monitoring**: Set up alerts for unusual activity

## Deployment Checklist

- [ ] Environment variables configured
- [ ] Database connection tested
- [ ] Static files collected
- [ ] Health checks working
- [ ] SSL certificate active
- [ ] Monitoring configured
- [ ] Backup strategy in place
- [ ] Performance testing completed
