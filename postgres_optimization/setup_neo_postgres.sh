#!/bin/bash

# PostgreSQL Setup Script for Neo (Local Development)
# Optimized for local development environment

set -e

echo "🚀 Setting up PostgreSQL for Neo (Local Development)..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
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

# Check if PostgreSQL is installed
check_postgresql() {
    print_status "Checking PostgreSQL installation..."
    
    if command -v psql &> /dev/null; then
        print_status "PostgreSQL is already installed"
        psql --version
    else
        print_status "Installing PostgreSQL..."
        
        # Detect OS and install PostgreSQL
        if [[ "$OSTYPE" == "linux-gnu"* ]]; then
            # Linux
            if command -v apt-get &> /dev/null; then
                # Ubuntu/Debian
                sudo apt-get update
                sudo apt-get install -y postgresql postgresql-contrib
            elif command -v yum &> /dev/null; then
                # CentOS/RHEL
                sudo yum install -y postgresql-server postgresql-contrib
                sudo postgresql-setup initdb
            fi
        elif [[ "$OSTYPE" == "darwin"* ]]; then
            # macOS
            if command -v brew &> /dev/null; then
                brew install postgresql
                brew services start postgresql
            else
                print_error "Please install Homebrew first: https://brew.sh/"
                exit 1
            fi
        else
            print_error "Unsupported operating system: $OSTYPE"
            exit 1
        fi
    fi
}

# Create database and user
setup_database() {
    print_status "Setting up database and user..."
    
    # Database configuration
    DB_NAME="monkhq_neo"
    DB_USER="monkhq_user"
    DB_PASSWORD="monkhq_dev_password_2024"
    
    # Start PostgreSQL service
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl start postgresql || sudo service postgresql start
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services start postgresql
    fi
    
    # Create user and database
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASSWORD';" || print_warning "User $DB_USER may already exist"
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" || print_warning "Database $DB_NAME may already exist"
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"
    
    print_status "Database '$DB_NAME' and user '$DB_USER' created successfully"
}

# Apply PostgreSQL configuration
apply_configuration() {
    print_status "Applying PostgreSQL configuration..."
    
    # Get PostgreSQL data directory
    PG_DATA=$(sudo -u postgres psql -t -c "SHOW data_directory;" | tr -d ' ')
    
    if [[ -z "$PG_DATA" ]]; then
        print_error "Could not determine PostgreSQL data directory"
        exit 1
    fi
    
    print_status "PostgreSQL data directory: $PG_DATA"
    
    # Backup original configuration
    CONFIG_FILE="$PG_DATA/postgresql.conf"
    if [[ -f "$CONFIG_FILE" ]]; then
        sudo cp "$CONFIG_FILE" "$CONFIG_FILE.backup.$(date +%Y%m%d_%H%M%S)"
        print_status "Original configuration backed up"
    fi
    
    # Copy optimized configuration
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    sudo cp "$SCRIPT_DIR/neo_postgres.conf" "$CONFIG_FILE"
    
    # Set proper permissions
    sudo chown postgres:postgres "$CONFIG_FILE"
    sudo chmod 644 "$CONFIG_FILE"
    
    print_status "Optimized configuration applied"
}

# Install required extensions
install_extensions() {
    print_status "Installing PostgreSQL extensions..."
    
    # Install extensions for the database
    sudo -u postgres psql -d monkhq_neo -c "CREATE EXTENSION IF NOT EXISTS pg_stat_statements;"
    sudo -u postgres psql -d monkhq_neo -c "CREATE EXTENSION IF NOT EXISTS pg_trgm;"
    sudo -u postgres psql -d monkhq_neo -c "CREATE EXTENSION IF NOT EXISTS unaccent;"
    sudo -u postgres psql -d monkhq_neo -c "CREATE EXTENSION IF NOT EXISTS pgcrypto;"
    
    print_status "Extensions installed successfully"
}

# Create performance monitoring functions
create_monitoring_functions() {
    print_status "Creating monitoring functions..."
    
    sudo -u postgres psql -d monkhq_neo << 'EOF'
-- Function to get database size
CREATE OR REPLACE FUNCTION get_database_size() 
RETURNS TEXT AS $$
BEGIN
    RETURN pg_size_pretty(pg_database_size(current_database()));
END;
$$ LANGUAGE plpgsql;

-- Function to get top queries
CREATE OR REPLACE FUNCTION get_top_queries(limit_cnt INTEGER DEFAULT 10)
RETURNS TABLE(query TEXT, calls BIGINT, total_time DOUBLE PRECISION, mean_time DOUBLE PRECISION) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        query,
        calls,
        total_exec_time,
        mean_exec_time
    FROM pg_stat_statements
    ORDER BY total_exec_time DESC
    LIMIT limit_cnt;
END;
$$ LANGUAGE plpgsql;

-- Function to get table sizes
CREATE OR REPLACE FUNCTION get_table_sizes()
RETURNS TABLE(schema_name TEXT, table_name TEXT, size TEXT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname,
        tablename,
        pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename))
    FROM pg_tables
    WHERE schemaname NOT IN ('information_schema', 'pg_catalog')
    ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC;
END;
$$ LANGUAGE plpgsql;

-- Function to get index usage
CREATE OR REPLACE FUNCTION get_index_usage()
RETURNS TABLE(schema_name TEXT, table_name TEXT, index_name TEXT, usage_count BIGINT) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        schemaname,
        tablename,
        indexname,
        idx_scan
    FROM pg_stat_user_indexes
    ORDER BY idx_scan DESC;
END;
$$ LANGUAGE plpgsql;
EOF
    
    print_status "Monitoring functions created"
}

# Restart PostgreSQL service
restart_postgresql() {
    print_status "Restarting PostgreSQL service..."
    
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        sudo systemctl restart postgresql || sudo service postgresql restart
    elif [[ "$OSTYPE" == "darwin"* ]]; then
        brew services restart postgresql
    fi
    
    print_status "PostgreSQL service restarted"
}

# Test connection
test_connection() {
    print_status "Testing database connection..."
    
    # Test connection with the new user
    PGPASSWORD="monkhq_dev_password_2024" psql -h localhost -U monkhq_user -d monkhq_neo -c "SELECT version();" > /dev/null 2>&1
    
    if [[ $? -eq 0 ]]; then
        print_status "Database connection successful!"
    else
        print_error "Database connection failed!"
        exit 1
    fi
}

# Create Django settings file
create_django_settings() {
    print_status "Creating Django settings file..."
    
    cat > "$(dirname "$0")/django_neo_settings.py" << 'EOF'
# Django PostgreSQL Settings for Neo (Local Development)
import os

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'monkhq_neo',
        'USER': 'monkhq_user',
        'PASSWORD': 'monkhq_dev_password_2024',
        'HOST': 'localhost',
        'PORT': '5432',
        'OPTIONS': {
            'connect_timeout': 10,
            'application_name': 'monkhq_neo',
        },
        'CONN_MAX_AGE': 600,  # 10 minutes
    }
}

# Database connection pooling
DATABASE_POOL_ARGS = {
    'max_overflow': 10,
    'pool_pre_ping': True,
    'pool_recycle': 300,
}

# Cache configuration (Redis)
CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.redis.RedisCache',
        'LOCATION': 'redis://localhost:6379/1',
        'OPTIONS': {
            'CLIENT_CLASS': 'django_redis.client.DefaultClient',
        }
    }
}

# Logging for database queries
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
        'file': {
            'class': 'logging.FileHandler',
            'filename': 'postgres_queries.log',
        },
    },
    'loggers': {
        'django.db.backends': {
            'handlers': ['console', 'file'],
            'level': 'DEBUG',
            'propagate': False,
        },
    },
}
EOF
    
    print_status "Django settings file created: $(dirname "$0")/django_neo_settings.py"
}

# Main execution
main() {
    print_status "Starting PostgreSQL setup for Neo..."
    
    check_postgresql
    setup_database
    apply_configuration
    install_extensions
    create_monitoring_functions
    restart_postgresql
    test_connection
    create_django_settings
    
    print_status "PostgreSQL setup for Neo completed successfully!"
    echo ""
    print_status "Connection details:"
    echo "  Host: localhost"
    echo "  Port: 5432"
    echo "  Database: monkhq_neo"
    echo "  User: monkhq_user"
    echo "  Password: monkhq_dev_password_2024"
    echo ""
    print_status "To connect to the database:"
    echo "  psql -h localhost -U monkhq_user -d monkhq_neo"
    echo ""
    print_status "Monitoring functions available:"
    echo "  SELECT * FROM get_database_size();"
    echo "  SELECT * FROM get_top_queries(10);"
    echo "  SELECT * FROM get_table_sizes();"
    echo "  SELECT * FROM get_index_usage();"
}

# Run main function
main "$@"
