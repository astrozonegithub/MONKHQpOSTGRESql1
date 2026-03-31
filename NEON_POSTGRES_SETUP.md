# Neon PostgreSQL Setup Guide for MonkHQ

## 🚀 Quick Setup with Neon

### Option 1: Using DATABASE_URL (Recommended)

1. **Create Neon Account**
   - Go to [neon.tech](https://neon.tech)
   - Sign up for a free account
   - Create a new PostgreSQL database

2. **Get Connection Details**
   - Copy the connection string from Neon dashboard
   - Format: `postgresql://username:password@hostname:5432/dbname`

3. **Configure Environment**
   ```bash
   # Copy environment template
   cp .env.example .env
   
   # Edit .env file
   nano .env
   
   # Add your Neon DATABASE_URL
   DATABASE_URL=postgresql://your_username:your_password@your_hostname.neon.tech:5432/your_dbname
   ```

4. **Install Dependencies**
   ```bash
   pip install psycopg2-binary python-dotenv
   ```

5. **Run Migrations**
   ```bash
   python manage.py migrate
   ```

6. **Start Development Server**
   ```bash
   python manage.py runserver
   ```

### Option 2: Manual Configuration

```bash
# Set individual environment variables
export DB_NAME=your_dbname
export DB_USER=your_username
export DB_PASSWORD=your_password
export DB_HOST=your_hostname.neon.tech
export DB_PORT=5432

# Run Django
python manage.py runserver
```

## 🔧 Configuration Details

### DATABASE_URL Parsing
The settings.py now parses the DATABASE_URL using:

```python
from urllib.parse import urlparse, parse_qsl

tmpPostgres = urlparse(os.getenv("DATABASE_URL"))

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': tmpPostgres.path.replace('/', ''),
        'USER': tmpPostgres.username,
        'PASSWORD': tmpPostgres.password,
        'HOST': tmpPostgres.hostname,
        'PORT': tmpPostgres.port or 5432,
        'OPTIONS': dict(parse_qsl(tmpPostgres.query)),
    }
}
```

### Supported URL Formats
```bash
# Basic Neon URL
postgresql://username:password@hostname.neon.tech:5432/dbname

# With SSL options
postgresql://username:password@hostname.neon.tech:5432/dbname?sslmode=require

# With connection pooling
postgresql://username:password@hostname.neon.tech:5432/dbname?sslmode=require&max_connections=20

# With application name
postgresql://username:password@hostname.neon.tech:5432/dbname?application_name=monkhq_app
```

## 🌐 Neon-Specific Features

### Connection Pooling
```bash
# Add pooling parameters to DATABASE_URL
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require&max_connections=20&connect_timeout=10"
```

### SSL Configuration
```bash
# Force SSL (recommended for Neon)
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
```

### Performance Options
```bash
# Optimize for Neon's serverless architecture
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require&application_name=monkhq_prod"
```

## 🐳 Docker with Neon

### Docker Compose Configuration
```yaml
version: '3.8'

services:
  django:
    build: .
    container_name: monkhq_django_neon
    environment:
      - DATABASE_URL=postgresql://your_username:your_password@your_hostname.neon.tech:5432/your_dbname?sslmode=require
      - SECRET_KEY=your-secret-key
      - DEBUG=True
      - ALLOWED_HOSTS=localhost,127.0.0.1
    ports:
      - "8000:8000"
    volumes:
      - .:/app
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    networks:
      - monkhq_network
    command: python manage.py runserver 0.0.0.0:8000
    restart: unless-stopped

volumes:
  static_volume:
  media_volume:

networks:
  monkhq_network:
    driver: bridge
```

### Docker Commands
```bash
# Build and run with Neon
docker-compose -f docker-compose-neon.yml up --build

# View logs
docker-compose -f docker-compose-neon.yml logs django

# Stop services
docker-compose -f docker-compose-neon.yml down
```

## 🔍 Testing Connection

### Test Neon Connection
```python
# test_neon_connection.py
import os
import psycopg2
from urllib.parse import urlparse

def test_neon_connection():
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not set")
        return False
    
    try:
        # Parse URL
        parsed = urlparse(DATABASE_URL)
        
        # Connect to Neon
        conn = psycopg2.connect(
            dbname=parsed.path.replace('/', ''),
            user=parsed.username,
            password=parsed.password,
            host=parsed.hostname,
            port=parsed.port or 5432,
            sslmode='require'
        )
        
        # Test query
        cursor = conn.cursor()
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✅ Connected to Neon PostgreSQL!")
        print(f"📋 Version: {version}")
        
        # Test database info
        cursor.execute("SELECT current_database(), current_user;")
        db_info = cursor.fetchone()
        print(f"🗄️  Database: {db_info[0]}")
        print(f"👤 User: {db_info[1]}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection failed: {e}")
        return False

if __name__ == "__main__":
    test_neon_connection()
```

### Run Connection Test
```bash
# Set DATABASE_URL
export DATABASE_URL="postgresql://your_username:your_password@your_hostname.neon.tech:5432/your_dbname"

# Test connection
python test_neon_connection.py
```

## 🚀 Production Deployment

### Environment Variables for Production
```bash
# Neon Production Database
DATABASE_URL=postgresql://prod_user:prod_password@prod_hostname.neon.tech:5432/prod_dbname?sslmode=require

# Django Production Settings
SECRET_KEY=your-production-secret-key
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com

# Additional Neon Options
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require&application_name=monkhq_prod&connect_timeout=30"
```

### Koyeb Deployment with Neon
```yaml
# koyeb-neon.yml
name: monkhq-neon
services:
  - name: monkhq-web
    source_dir: .
    build_command: |
      pip install -r requirements.txt
      python manage.py collectstatic --noinput
    run_command: gunicorn monkhq.wsgi:application --bind 0.0.0.0:$PORT
    environment_variables:
      - key: DATABASE_URL
        value: postgresql://your_username:your_password@your_hostname.neon.tech:5432/your_dbname?sslmode=require
      - key: SECRET_KEY
        value: your-production-secret-key
      - key: DEBUG
        value: "False"
      - key: ALLOWED_HOSTS
        value: "*.koyeb.app,monkhq.com,www.monkhq.com"
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
```

## 📊 Monitoring Neon Performance

### Neon-Specific Queries
```sql
-- Check Neon connection info
SELECT 
    application_name,
    client_addr,
    state,
    query_start,
    state_change
FROM pg_stat_activity 
WHERE application_name = 'monkhq_app';

-- Monitor Neon-specific metrics
SELECT 
    datname,
    numbackends,
    xact_commit,
    xact_rollback,
    blks_read,
    blks_hit,
    tup_returned,
    tup_fetched,
    tup_inserted,
    tup_updated,
    tup_deleted
FROM pg_stat_database 
WHERE datname = current_database();

-- Check Neon storage usage
SELECT 
    pg_size_pretty(pg_database_size(current_database())) as database_size,
    pg_size_pretty(pg_total_relation_size('pg_class')) as total_size;
```

### Django Management Commands
```bash
# Check database connection
python manage.py dbshell

# Run migrations on Neon
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Collect static files
python manage.py collectstatic --noinput

# Check Django configuration
python manage.py check --database default
```

## 🔧 Troubleshooting

### Common Neon Issues

#### Connection Timeout
```bash
# Add timeout to DATABASE_URL
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require&connect_timeout=30"
```

#### SSL Certificate Issues
```bash
# Force SSL mode
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require"
```

#### Performance Issues
```bash
# Add connection pooling
DATABASE_URL="postgresql://user:pass@host:5432/db?sslmode=require&max_connections=20"
```

### Debug Connection
```python
# debug_neon.py
import os
from urllib.parse import urlparse

DATABASE_URL = os.getenv("DATABASE_URL")
parsed = urlparse(DATABASE_URL)

print("🔍 Neon Database Configuration:")
print(f"   Host: {parsed.hostname}")
print(f"   Port: {parsed.port}")
print(f"   Database: {parsed.path.replace('/', '')}")
print(f"   User: {parsed.username}")
print(f"   SSL Mode: {dict(parse_qsl(parsed.query)).get('sslmode', 'prefer')}")
print(f"   Application Name: {dict(parse_qsl(parsed.query)).get('application_name', 'monkhq_app')}")
```

## 🎯 Best Practices for Neon

### Performance Optimization
1. **Use connection pooling** for better performance
2. **Enable SSL** for all connections
3. **Set application name** for better monitoring
4. **Use appropriate timeouts** for serverless architecture
5. **Monitor connection usage** to avoid limits

### Security Best Practices
1. **Never commit DATABASE_URL** to version control
2. **Use environment variables** for configuration
3. **Enable SSL** for all connections
4. **Use strong passwords** for database users
5. **Regularly rotate** database credentials

### Development Workflow
1. **Use separate databases** for development and production
2. **Test connection** before running migrations
3. **Backup regularly** using Neon's backup features
4. **Monitor performance** using Neon's dashboard
5. **Use connection pooling** in production

---

## 🎉 Summary

Your MonkHQ application is now optimized for **Neon PostgreSQL** with:

✅ **DATABASE_URL parsing** for easy configuration  
✅ **SSL support** for secure connections  
✅ **Connection pooling** for better performance  
✅ **Environment variable support** for security  
✅ **Docker integration** for containerized deployment  
✅ **Production-ready** configuration  
✅ **Monitoring tools** for performance tracking  

**Start using Neon PostgreSQL with MonkHQ today!** 🚀
