#!/bin/bash

# PostgreSQL Setup Script for Koyeb Production
# Optimized for Koyeb cloud environment

set -e

echo "🚀 Setting up PostgreSQL for Koyeb Production..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

print_koyeb() {
    echo -e "${BLUE}[KOYEB]${NC} $1"
}

# Koyeb environment variables
setup_koyeb_env() {
    print_koyeb "Setting up Koyeb environment variables..."
    
    # Database configuration from Koyeb environment
    export KOYEB_DB_HOST="${KOYEB_DB_HOST:-localhost}"
    export KOYEB_DB_PORT="${KOYEB_DB_PORT:-5432}"
    export KOYEB_DB_NAME="${KOYEB_DB_NAME:-monkhq_koyeb}"
    export KOYEB_DB_USER="${KOYEB_DB_USER:-monkhq_user}"
    export KOYEB_DB_PASSWORD="${KOYEB_DB_PASSWORD}"
    
    if [[ -z "$KOYEB_DB_PASSWORD" ]]; then
        print_error "KOYEB_DB_PASSWORD environment variable is required"
        exit 1
    fi
    
    print_status "Koyeb environment configured"
}

# Create database and user for Koyeb
setup_koyeb_database() {
    print_status "Setting up Koyeb database and user..."
    
    # Connect to PostgreSQL and create database
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U postgres -c "CREATE USER $KOYEB_DB_USER WITH PASSWORD '$KOYEB_DB_PASSWORD';" || print_warning "User $KOYEB_DB_USER may already exist"
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U postgres -c "CREATE DATABASE $KOYEB_DB_NAME OWNER $KOYEB_DB_USER;" || print_warning "Database $KOYEB_DB_NAME may already exist"
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U postgres -c "GRANT ALL PRIVILEGES ON DATABASE $KOYEB_DB_NAME TO $KOYEB_DB_USER;"
    
    print_status "Koyeb database '$KOYEB_DB_NAME' and user '$KOYEB_DB_USER' created successfully"
}

# Apply Koyeb-specific configuration
apply_koyeb_configuration() {
    print_status "Applying Koyeb PostgreSQL configuration..."
    
    # Get PostgreSQL data directory on Koyeb
    PG_DATA=$(psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U postgres -t -c "SHOW data_directory;" | tr -d ' ')
    
    if [[ -z "$PG_DATA" ]]; then
        print_error "Could not determine PostgreSQL data directory"
        exit 1
    fi
    
    print_status "PostgreSQL data directory: $PG_DATA"
    
    # Backup original configuration
    CONFIG_FILE="$PG_DATA/postgresql.conf"
    if [[ -f "$CONFIG_FILE" ]]; then
        cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Original configuration backed up"
    fi
    
    # Copy optimized Koyeb configuration
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    cp "$SCRIPT_DIR/koyeb_postgres.conf" "$CONFIG_FILE"
    
    print_status "Koyeb optimized configuration applied"
}

# Install production extensions
install_koyeb_extensions() {
    print_status "Installing Koyeb PostgreSQL extensions..."
    
    # Install extensions for the database
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS unaccent;"
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS btree_gin;"
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "CREATE EXTENSION IF NOT EXISTS btree_gist;"
    
    print_status "Koyeb extensions installed successfully"
}

# Create production monitoring functions
create_koyeb_monitoring() {
    print_status "Creating Koyeb production monitoring functions..."
    
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" << 'EOF'
-- Production monitoring functions for Koyeb

-- Function to get database health status
CREATE OR REPLACE FUNCTION get_database_health()
RETURNS TABLE(metric TEXT, value TEXT, status TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'Database Size'::TEXT,
        pg_size_pretty(pg_database_size(current_database()))::TEXT,
        CASE 
            WHEN pg_database_size(current_database()) > 1073741824 THEN 'WARNING' -- > 1GB
            ELSE 'OK'
        END::TEXT
    UNION ALL
    SELECT 
        'Active Connections'::TEXT,
        count(*)::TEXT,
        CASE 
            WHEN count(*) > 150 THEN 'CRITICAL'
            WHEN count(*) > 100 THEN 'WARNING'
            ELSE 'OK'
        END::TEXT
    FROM pg_stat_activity
    WHERE state = 'active'
    UNION ALL
    SELECT 
        'Cache Hit Ratio'::TEXT,
        ROUND((sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100, 2)::TEXT,
        CASE 
            WHEN (sum(heap_blks_hit) / NULLIF(sum(heap_blks_hit) + sum(heap_blks_read), 0)) * 100 < 95 THEN 'WARNING'
            ELSE 'OK'
        END::TEXT
    FROM pg_stat_database
    WHERE datname = current_database();
END;
$$ LANGUAGE plpgsql;

-- Function to get slow queries
CREATE OR REPLACE FUNCTION get_slow_queries(limit_cnt INTEGER DEFAULT 20)
RETURNS TABLE(query TEXT, calls BIGINT, total_time DOUBLE PRECISION, mean_time DOUBLE PRECISION, rows BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        LEFT(query, 200) as query,
        calls,
        total_exec_time,
        mean_exec_time,
        rows
    FROM pg_stat_statements
    WHERE mean_exec_time > 100  -- queries taking more than 100ms on average
    ORDER BY mean_exec_time DESC
    LIMIT limit_cnt;
END;
$$ LANGUAGE plpgsql;

-- Function to get table bloat analysis
CREATE OR REPLACE FUNCTION get_table_bloat()
RETURNS TABLE(schema_name TEXT, table_name TEXT, bloat_percentage DOUBLE PRECISION, wasted_space TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname,
        tablename,
        ROUND((tuples * 24 - pg_total_relation_size(schemaname||'.'||tablename)) / pg_total_relation_size(schemaname||'.'||tablename) * 100, 2) as bloat_percentage,
        pg_size_pretty((tuples * 24 - pg_total_relation_size(schemaname||'.'||tablename))) as wasted_space
    FROM pg_stat_user_tables
    WHERE (tuples * 24 - pg_total_relation_size(schemaname||'.'||tablename)) > 0
    ORDER BY bloat_percentage DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get index efficiency
CREATE OR REPLACE FUNCTION get_index_efficiency()
RETURNS TABLE(schema_name TEXT, table_name TEXT, index_name TEXT, efficiency DOUBLE PRECISION, recommendation TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname,
        tablename,
        indexname,
        CASE 
            WHEN idx_scan = 0 THEN 0.0
            ELSE ROUND((idx_scan::FLOAT / (seq_scan + idx_scan)) * 100, 2)
        END as efficiency,
        CASE 
            WHEN idx_scan = 0 THEN 'Consider dropping unused index'
            WHEN (idx_scan::FLOAT / (seq_scan + idx_scan)) * 100 < 10 THEN 'Low usage - review necessity'
            ELSE 'Good usage'
        END as recommendation
    FROM pg_stat_user_indexes
    ORDER BY efficiency ASC;
END;
$$ LANGUAGE plpgsql;

-- Function to get connection statistics
CREATE OR REPLACE FUNCTION get_connection_stats()
RETURNS TABLE(state TEXT, count BIGINT, percentage DOUBLE PRECISION) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        state,
        count(*)::BIGINT,
        ROUND((count(*)::FLOAT / (SELECT count(*) FROM pg_stat_activity)) * 100, 2)
    FROM pg_stat_activity
    GROUP BY state
    ORDER BY count DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get replication status (if applicable)
CREATE OR REPLACE FUNCTION get_replication_status()
RETURNS TABLE(status TEXT, lag_time INTERVAL) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        'Streaming'::TEXT,
        pg_last_xact_replay_timestamp() - now()
    FROM pg_stat_replication
    UNION ALL
    SELECT 
        'Not Replicating'::TEXT,
        INTERVAL '0'
    WHERE NOT EXISTS (SELECT 1 FROM pg_stat_replication);
END;
$$ LANGUAGE plpgsql;
EOF
    
    print_status "Koyeb production monitoring functions created"
}

# Create backup procedures
create_backup_procedures() {
    print_status "Creating backup procedures for Koyeb..."
    
    psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" << 'EOF'
-- Backup procedures for Koyeb

-- Function to create database backup
CREATE OR REPLACE FUNCTION create_backup(backup_name TEXT DEFAULT NULL)
RETURNS TEXT AS $$
DECLARE
    backup_file TEXT;
    timestamp TEXT;
BEGIN
    timestamp := to_char(now(), 'YYYY_MM_DD_HH24_MI_SS');
    backup_name := COALESCE(backup_name, 'backup_' || timestamp);
    backup_file := '/tmp/' || backup_name || '.sql';
    
    -- This would be executed by an external script
    -- pg_dump -h $KOYEB_DB_HOST -U $KOYEB_DB_USER -d $KOYEB_DB_NAME > backup_file
    
    RETURN backup_file;
END;
$$ LANGUAGE plpgsql;

-- Function to get backup status
CREATE OR REPLACE FUNCTION get_backup_status()
RETURNS TABLE(last_backup TIMESTAMP, backup_size TEXT, status TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        now() as last_backup,
        'N/A' as backup_size,
        'Manual backup required' as status;
END;
$$ LANGUAGE plpgsql;
EOF
    
    print_status "Backup procedures created"
}

# Restart PostgreSQL service on Koyeb
restart_koyeb_postgresql() {
    print_status "Restarting PostgreSQL service on Koyeb..."
    
    # On Koyeb, PostgreSQL is managed by the platform
    # This would typically be done via the Koyeb dashboard or API
    print_koyeb "PostgreSQL restart should be done via Koyeb dashboard"
    print_koyeb "Or use: koyeb service restart postgresql-service"
}

# Test Koyeb connection
test_koyeb_connection() {
    print_status "Testing Koyeb database connection..."
    
    # Test connection with the Koyeb user
    PGPASSWORD="$KOYEB_DB_PASSWORD" psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "SELECT version();" > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        print_status "Koyeb database connection successful!"
    else
        print_error "Koyeb database connection failed!"
        exit 1
    fi
}

# Create Django settings for Koyeb
create_koyeb_django_settings() {
    print_status "Creating Django settings file for Koyeb..."
    
    cat > "$(dirname "$0")/django_koyeb_settings.py" << 'EOF'
# Django PostgreSQL Settings for Koyeb Production
import os

# Database configuration for Koyeb
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('KOYEB_DB_NAME', 'monkhq_koyeb'),
        'USER': os.environ.get('KOYEB_DB_USER', 'monkhq_user'),
        'PASSWORD': os.environ.get('KOYEB_DB_PASSWORD'),
        'HOST': os.environ.get('KOYEB_DB_HOST', 'localhost'),
        'PORT': os.environ.get('KOYEB_DB_PORT', '5432'),
        'OPTIONS': {
            'connect_timeout': 30,
            'application_name': 'monkhq_koyeb',
            'sslmode': 'require',
        },
        'CONN_MAX_AGE': 600,  # 10 minutes
    }
}

# Database connection pooling for production
DATABASE_POOL_ARGS = {
    'max_overflow': 20,
    'pool_pre_ping': True,
    'pool_recycle': 300,
    'pool_timeout': 30,
}

# Cache configuration (Redis on Koyeb)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': os.environ.get('REDIS_URL', 'redis://localhost:6379/1'),
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
            'CONNECTION_POOL_KWARGS': {
                'max_connections': 50,
                'retry_on_timeout': True,
            }
        }
    }
}

# Production logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'formatters': {
        'verbose': {
            'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
            'style': '{',
        },
    },
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
            'formatter': 'verbose',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': '/app/logs/django.log',
            'formatter': 'verbose',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'WARNING',
            'propagate': False,
        },
        'monkhq': {
            'handlers': ['console', 'file'],
            'level': 'INFO',
            'propagate': False,
        },
    },
}

# Database health check middleware
DATABASE_HEALTH_CHECK = True

# Connection timeout settings
DATABASE_TIMEOUT = 30
DATABASE_HEALTH_CHECK_INTERVAL = 60
EOF
    
    print_status "Django Koyeb settings file created: $(dirname "$0")/django_koyeb_settings.py"
}

# Create Koyeb deployment script
create_koyeb_deployment_script() {
    print_status "Creating Koyeb deployment script..."
    
    cat > "$(dirname "$0")/koyeb_deploy.sh" << 'EOF'
#!/bin/bash

# Koyeb PostgreSQL Deployment Script

set -e

echo "🚀 Deploying PostgreSQL optimizations to Koyeb..."

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_koyeb() {
    echo -e "${BLUE}[KOYEB]${NC} $1"
}

# Check Koyeb CLI
if ! command -v koyeb &> /dev/null; then
    echo "Koyeb CLI not found. Please install it first:"
    echo "curl -sL https://github.com/koyeb/koyeb-cli/releases/latest/download/koyeb-linux-amd64 -o koyeb"
    echo "chmod +x koyeb"
    echo "sudo mv koyeb /usr/local/bin/"
    exit 1
fi

# Get Koyeb service information
SERVICE_NAME=$(koyeb service list | grep postgresql | head -1 | awk '{print $1}')

if [[ -z "$SERVICE_NAME" ]]; then
    print_koyeb "No PostgreSQL service found. Please create one first."
    exit 1
fi

print_koyeb "Found PostgreSQL service: $SERVICE_NAME"

# Apply configuration (this would need to be done via Koyeb's interface)
print_koyeb "Configuration should be applied via Koyeb dashboard or API"
print_koyeb "Service: $SERVICE_NAME"
print_koyeb "Config file: koyeb_postgres.conf"

# Test connection
print_status "Testing connection..."
PGPASSWORD="$KOYEB_DB_PASSWORD" psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "SELECT version();"

# Run health check
print_status "Running health check..."
PGPASSWORD="$KOYEB_DB_PASSWORD" psql -h "$KOYEB_DB_HOST" -p "$KOYEB_DB_PORT" -U "$KOYEB_DB_USER" -d "$KOYEB_DB_NAME" -c "SELECT * FROM get_database_health();"

print_status "Koyeb PostgreSQL deployment completed!"
EOF
    
    chmod +x "$(dirname "$0")/koyeb_deploy.sh"
    print_status "Koyeb deployment script created: $(dirname "$0")/koyeb_deploy.sh"
}

# Main execution
main() {
    print_status "Starting PostgreSQL setup for Koyeb..."
    
    setup_koyeb_env
    setup_koyeb_database
    apply_koyeb_configuration
    install_koyeb_extensions
    create_koyeb_monitoring
    create_backup_procedures
    restart_koyeb_postgresql
    test_koyeb_connection
    create_koyeb_django_settings
    create_koyeb_deployment_script
    
    print_status "PostgreSQL setup for Koyeb completed successfully!"
    echo ""
    print_status "Connection details:"
    echo "  Host: $KOYEB_DB_HOST"
    echo "  Port: $KOYEB_DB_PORT"
    echo "  Database: $KOYEB_DB_NAME"
    echo "  User: $KOYEB_DB_USER"
    echo ""
    print_status "Production monitoring functions available:"
    echo "  SELECT * FROM get_database_health();"
    echo "  SELECT * FROM get_slow_queries(20);"
    echo "  SELECT * FROM get_table_bloat();"
    echo "  SELECT * FROM get_index_efficiency();"
    echo "  SELECT * FROM get_connection_stats();"
    echo "  SELECT * FROM get_replication_status();"
    echo ""
    print_koyeb "To apply configuration on Koyeb:"
    echo "  1. Use Koyeb dashboard to upload koyeb_postgres.conf"
    echo "  2. Or use Koyeb API to update service configuration"
    echo "  3. Restart the PostgreSQL service"
}

# Run main function
main "$@"
