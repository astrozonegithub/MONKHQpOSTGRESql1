# PostgreSQL Setup Guide for MonkHQ

## 🚀 Quick Start

### Option 1: Docker Compose (Recommended)

```bash
# Start PostgreSQL and Redis with optimized configuration
docker-compose -f docker-compose-postgres.yml up -d

# Run MonkHQ with PostgreSQL
docker-compose -f docker-compose-postgres.yml exec django python manage.py runserver 0.0.0.0:8000
```

### Option 2: Local PostgreSQL

```bash
# Install PostgreSQL dependencies
pip install psycopg2-binary python-dotenv

# Copy environment file
cp .env.example .env

# Edit .env with your database credentials
nano .env

# Run setup script
python setup_postgres.py

# Start Django
python manage.py runserver
```

### Option 3: Manual Setup

```bash
# Connect to PostgreSQL
psql -U postgres

# Create database and user
CREATE DATABASE monkhq;
CREATE USER monkhq_user WITH PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE monkhq TO monkhq_user;

# Install extensions
\c monkhq
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;
CREATE EXTENSION IF NOT EXISTS pg_trgm;
CREATE EXTENSION IF NOT EXISTS unaccent;
CREATE EXTENSION IF NOT EXISTS pgcrypto;

# Run Django migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser
```

## 📁 Files Created/Modified

### Configuration Files
- **`monkhq/settings.py`** - Updated with PostgreSQL configuration
- **`.env.example`** - Environment variables template
- **`requirements.txt`** - Updated with psycopg2-binary and python-dotenv

### Setup Scripts
- **`setup_postgres.py`** - Automated database setup script
- **`docker-compose-postgres.yml`** - Docker Compose configuration

### Documentation
- **`POSTGRES_SETUP_GUIDE.md`** - This setup guide

## ⚙️ Configuration Details

### Database Settings (settings.py)
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DB_NAME', 'monkhq'),
        'USER': os.environ.get('DB_USER', 'monkhq_user'),
        'PASSWORD': os.environ.get('DB_PASSWORD', 'monkhq_password'),
        'HOST': os.environ.get('DB_HOST', 'localhost'),
        'PORT': os.environ.get('DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 10,
            'application_name': 'monkhq_django',
        },
        'CONN_MAX_AGE': 600,  # 10 minutes - persistent connections
    }
}
```

### Environment Variables (.env)
```bash
# Database Configuration
DB_NAME=monkhq
DB_USER=monkhq_user
DB_PASSWORD=your_secure_password_here
DB_HOST=localhost
DB_PORT=5432

# Django Configuration
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Optional: Redis Cache
REDIS_URL=redis://localhost:6379/1
```

## 🔧 Features Enabled

### PostgreSQL Extensions
- **pg_stat_statements** - Query performance tracking
- **pg_trgm** - Trigram text search
- **unaccent** - Accent-insensitive search
- **pgcrypto** - Cryptographic functions

### Monitoring Functions
- **get_database_size()** - Get current database size
- **get_connection_info()** - Connection statistics
- **get_table_sizes()** - Table size analysis

### Django Optimizations
- **Connection Pooling** - 10-minute persistent connections
- **Application Name** - Track connections in PostgreSQL
- **Connect Timeout** - 10-second connection timeout

## 🐳 Docker Compose Features

### Services
- **PostgreSQL 15** - Latest stable version with optimizations
- **Redis 7** - For caching and sessions
- **Django** - MonkHQ application

### Optimizations
- **Custom Configuration** - Uses neo_postgres.conf
- **Health Checks** - Ensures services are ready
- **Persistent Volumes** - Data persistence
- **Network Isolation** - Secure internal networking

### Environment Variables
- **Database Credentials** - Secure credential management
- **Redis Connection** - Cache configuration
- **Django Settings** - Development configuration

## 📊 Monitoring & Maintenance

### Database Monitoring
```sql
-- Check database size
SELECT get_database_size();

-- View connection info
SELECT * FROM get_connection_info();

-- Analyze table sizes
SELECT * FROM get_table_sizes();

-- Check slow queries
SELECT query, calls, mean_exec_time 
FROM pg_stat_statements 
ORDER BY mean_exec_time DESC 
LIMIT 10;
```

### Django Management Commands
```bash
# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic

# Check database integrity
python manage.py check --database default
```

## 🔍 Troubleshooting

### Connection Issues
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# Test connection manually
psql -h localhost -U monkhq_user -d monkhq
```

### Docker Issues
```bash
# Check container logs
docker-compose -f docker-compose-postgres.yml logs postgres
docker-compose -f docker-compose-postgres.yml logs django

# Restart services
docker-compose -f docker-compose-postgres.yml restart

# Rebuild containers
docker-compose -f docker-compose-postgres.yml down
docker-compose -f docker-compose-postgres.yml up --build
```

### Django Issues
```bash
# Check Django settings
python manage.py diffsettings

# Test database connection
python manage.py dbshell

# Check migrations status
python manage.py showmigrations
```

## 🚀 Production Deployment

### Environment Variables for Production
```bash
# Database
DB_NAME=monkhq_production
DB_USER=monkhq_user
DB_PASSWORD=your_production_password
DB_HOST=your_production_host
DB_PORT=5432

# Security
SECRET_KEY=your_production_secret_key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Cache
REDIS_URL=redis://your-redis-host:6379/1
```

### Production Optimizations
- Use the **koyeb_postgres.conf** configuration
- Enable SSL connections
- Set up read replicas
- Configure connection pooling
- Enable query logging
- Set up monitoring and alerts

## 📚 Additional Resources

### Documentation
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Django Database Settings](https://docs.djangoproject.com/en/stable/ref/databases/)
- [psycopg2 Documentation](https://www.psycopg.org/docs/)

### Performance Tuning
- [PostgreSQL Performance Tuning](https://wiki.postgresql.org/wiki/Tuning_Your_PostgreSQL_Server)
- [Django Database Optimization](https://docs.djangoproject.com/en/stable/topics/db/optimization/)

### Monitoring Tools
- [pgAdmin](https://www.pgadmin.org/)
- [PostgreSQL Metrics](https://github.com/spotify/postgresql-metrics)
- [Django Debug Toolbar](https://github.com/jazzband/django-debug-toolbar)

## 🎯 Best Practices

### Development
1. **Use environment variables** for sensitive data
2. **Run migrations** after model changes
3. **Test connections** before deployment
4. **Monitor performance** during development
5. **Backup regularly** even in development

### Production
1. **Use strong passwords** and secure connections
2. **Enable SSL** for all database connections
3. **Set up monitoring** and alerting
4. **Regular backups** and recovery testing
5. **Connection pooling** for performance

### Security
1. **Never commit** credentials to version control
2. **Use environment variables** for configuration
3. **Limit database access** to required users
4. **Enable logging** for security auditing
5. **Regular updates** of PostgreSQL and dependencies

---

## 🎉 Summary

Your MonkHQ application is now configured to use PostgreSQL with:

✅ **Production-ready database configuration**  
✅ **Automated setup scripts** for easy deployment  
✅ **Docker Compose** for development environment  
✅ **Monitoring functions** for performance tracking  
✅ **Optimized settings** for both development and production  
✅ **Complete documentation** for maintenance and troubleshooting  

**Start using PostgreSQL with MonkHQ today!** 🚀
