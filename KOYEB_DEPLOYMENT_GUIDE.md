# 🚀 MonkHQ Koyeb Deployment Guide

## 📋 **Prerequisites**

- **Koyeb Account**: Create account at [koyeb.com](https://koyeb.com)
- **GitHub Repository**: Push your code to GitHub
- **Neon Database**: Active Neon PostgreSQL database
- **Domain**: Optional custom domain

## 🔧 **Configuration Files**

### **1. koyeb.yaml** (Optimized for Koyeb)
```yaml
name: monkhq
services:
  - name: monkhq-web
    source_dir: .
    build_command: |
      pip install --upgrade pip
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
      python manage.py migrate --noinput
    run_command: gunicorn monkhq.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120
    environment_variables:
      - key: DJANGO_SETTINGS_MODULE
        value: monkhq.settings
      - key: SECRET_KEY
        value: django-insecure-change-this-in-production-replace-with-secure-key
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        value: "*.koyeb.app,monkhq.com,www.monkhq.com"
      - key: DATABASE_URL
        value: postgresql://neondb_owner:npg_OKZUyG06jRIE@ep-tiny-field-an0w3uqj-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
      - key: REDIS_URL
        value: redis://redis:6379/1
      - key: EMAIL_HOST
        value: smtp.gmail.com
      - key: EMAIL_PORT
        value: "587"
      - key: EMAIL_USE_TLS
        value: "True"
      - key: DEFAULT_FROM_EMAIL
        value: hello@monkhq.com
    instance_type: nano
    ports:
      - port: 8000
        protocol: http
    routes:
      - path: /
    health_check:
      path: /
      port: 8000
      protocol: http
      grace_period: 10
      check_interval: 15
      timeout: 5
    scaling:
      min: 1
      max: 3
      target_cpu_percent: 70
    regions:
      - was
      - fra
      - sin
  - name: redis
    image: redis:7-alpine
    instance_type: nano
    ports:
      - port: 6379
        protocol: tcp
    scaling:
      min: 1
      max: 1
```

### **2. Dockerfile** (Simplified for Koyeb)
```dockerfile
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

RUN mkdir -p staticfiles media logs
RUN python manage.py collectstatic --noinput || true

EXPOSE 8000

CMD gunicorn monkhq.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
```

### **3. requirements.txt** (Optimized)
```txt
# Core Django
Django==5.1.15
gunicorn==21.2.0

# Database
psycopg2-binary==2.9.9
python-dotenv==1.0.0

# Static files and middleware
whitenoise==6.6.0

# Forms and UI
django-crispy-forms==2.1
crispy-bootstrap5==0.7
Pillow==10.1.0

# API and CORS
djangorestframework==3.14.0
django-cors-headers==4.3.1

# Cache and sessions
redis==5.0.1

# Development tools (optional for production)
django-extensions==3.2.3

# Email
django-environ==0.11.2

# Monitoring (optional)
sentry-sdk==1.38.0
```

## 🚀 **Deployment Steps**

### **Step 1: Push to GitHub**
```bash
git init
git add .
git commit -m "Optimize for Koyeb deployment"
git branch -M main
git remote add origin https://github.com/yourusername/monkhq.git
git push -u origin main
```

### **Step 2: Deploy to Koyeb**

1. **Login to Koyeb Dashboard**
2. **Click "Create App"**
3. **Select "GitHub" as source**
4. **Choose your repository**
5. **Select "Use koyeb.yaml"**
6. **Review configuration**
7. **Click "Deploy"**

### **Step 3: Configure Environment Variables**

**Required Variables:**
- `SECRET_KEY`: Generate secure key
- `DATABASE_URL`: Your Neon connection string
- `ALLOWED_HOSTS`: Your domain and Koyeb subdomain

**Optional Variables:**
- `EMAIL_HOST_USER`: Gmail username
- `EMAIL_HOST_PASSWORD`: Gmail app password
- `SENTRY_DSN`: Error tracking

## 🔧 **Environment Variables Setup**

### **Generate SECRET_KEY:**
```python
# In Django shell
from django.core.management.utils import get_random_secret_key
print(get_random_secret_key())
```

### **Neon DATABASE_URL:**
```bash
DATABASE_URL=postgresql://neondb_owner:npg_OKZUyG06jRIE@ep-tiny-field-an0w3uqj-pooler.c-6.us-east-1.aws.neon.tech/neondb?sslmode=require&channel_binding=require
```

### **ALLOWED_HOSTS:**
```bash
ALLOWED_HOSTS=your-app-name.koyeb.app,yourdomain.com,www.yourdomain.com
```

## 🌐 **Custom Domain Setup**

### **Step 1: Add Domain in Koyeb**
1. Go to your app settings
2. Click "Domains"
3. Add your custom domain
4. Verify DNS records

### **Step 2: Update ALLOWED_HOSTS**
```bash
ALLOWED_HOSTS=your-app-name.koyeb.app,yourdomain.com,www.yourdomain.com
```

### **Step 3: DNS Configuration**
```
A record: yourdomain.com -> Koyeb IP
CNAME record: www -> yourdomain.com
```

## 📊 **Monitoring and Logs**

### **Health Check**
- **Endpoint**: `https://your-app.koyeb.app/health/`
- **Response**: `{"status": "healthy", "version": "1.0.0", "service": "monkhq"}`

### **Logs**
- **Koyeb Dashboard**: Real-time logs
- **Django Logs**: Configured for production
- **Error Tracking**: Sentry integration available

### **Performance**
- **Auto-scaling**: 1-3 instances based on CPU
- **Regions**: WAS, FRA, SIN (global)
- **Redis Cache**: Session and caching

## 🔒 **Security Settings**

### **Production Security:**
- `DEBUG = False`
- `SECURE_SSL_REDIRECT = True`
- `SESSION_COOKIE_SECURE = True`
- `CSRF_COOKIE_SECURE = True`
- `SECURE_HSTS_SECONDS = 31536000`

### **Database Security:**
- SSL connection required
- Channel binding enabled
- Connection pooling active

## 🚨 **Troubleshooting**

### **Build Failures:**
1. **Check requirements.txt** - Remove conflicting packages
2. **Update pip version** - Use latest pip
3. **Check Python version** - Use 3.11
4. **Verify system dependencies** - libpq-dev required

### **Runtime Errors:**
1. **Database connection** - Verify DATABASE_URL
2. **Static files** - Run collectstatic
3. **Migrations** - Apply database migrations
4. **Environment variables** - Check all required vars

### **Performance Issues:**
1. **Workers** - Adjust gunicorn workers
2. **Timeout** - Increase timeout for long requests
3. **Memory** - Upgrade instance type if needed
4. **Cache** - Verify Redis connection

## 📈 **Optimization Tips**

### **Performance:**
- Use Redis for sessions and caching
- Enable compression for static files
- Optimize database queries
- Use CDN for static assets

### **Cost:**
- Use nano instances for development
- Scale based on traffic
- Monitor resource usage
- Optimize build time

### **Reliability:**
- Enable health checks
- Set up monitoring
- Use multiple regions
- Implement error tracking

## 🎯 **Post-Deployment Checklist**

- [ ] Application loads correctly
- [ ] Database connection working
- [ ] Static files serving
- [ ] Admin panel accessible
- [ ] Health check responding
- [ ] Custom domain configured
- [ ] SSL certificate active
- [ ] Error monitoring setup
- [ ] Backup strategy in place
- [ ] Performance monitoring active

## 📞 **Support**

- **Koyeb Documentation**: [docs.koyeb.com](https://docs.koyeb.com)
- **Django Documentation**: [docs.djangoproject.com](https://docs.djangoproject.com)
- **Neon Documentation**: [neon.tech/docs](https://neon.tech/docs)
- **Community**: Join Koyeb Discord community

---

## 🎉 **Ready to Deploy!**

Your MonkHQ application is now **optimized for Koyeb hosting** with:

✅ **Simplified Dockerfile** for reliable builds  
✅ **Optimized requirements.txt** for faster installation  
✅ **Production-ready koyeb.yaml** configuration  
✅ **Health check endpoint** for monitoring  
✅ **Environment variable configuration**  
✅ **Auto-scaling and multi-region support**  
✅ **Redis caching and sessions**  
✅ **SSL security and performance optimizations**  

**Deploy to Koyeb and enjoy serverless hosting!** 🚀
