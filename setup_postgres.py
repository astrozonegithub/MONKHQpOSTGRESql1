#!/usr/bin/env python3
"""
PostgreSQL Database Setup Script for MonkHQ
Automates database creation and configuration
"""

import os
import sys
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from django.core.management import execute_from_command_line
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

def setup_database():
    """Setup PostgreSQL database for MonkHQ"""
    
    print("🚀 Setting up PostgreSQL database for MonkHQ...")
    
    # Database configuration
    db_name = os.environ.get('DB_NAME', 'monkhq')
    db_user = os.environ.get('DB_USER', 'monkhq_user')
    db_password = os.environ.get('DB_PASSWORD', 'monkhq_password')
    db_host = os.environ.get('DB_HOST', 'localhost')
    db_port = os.environ.get('DB_PORT', '5432')
    
    print(f"Database: {db_name}")
    print(f"User: {db_user}")
    print(f"Host: {db_host}")
    print(f"Port: {db_port}")
    
    try:
        # Connect to PostgreSQL server (default postgres database)
        conn = psycopg2.connect(
            dbname='postgres',
            user='postgres',
            host=db_host,
            port=db_port,
            password=os.environ.get('POSTGRES_PASSWORD', '')
        )
        conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
        cursor = conn.cursor()
        
        # Create user if not exists
        try:
            cursor.execute(f"CREATE USER {db_user} WITH PASSWORD '{db_password}';")
            print(f"✅ Created user: {db_user}")
        except psycopg2.errors.DuplicateObject:
            print(f"ℹ️  User {db_user} already exists")
        
        # Create database if not exists
        try:
            cursor.execute(f"CREATE DATABASE {db_name} OWNER {db_user};")
            print(f"✅ Created database: {db_name}")
        except psycopg2.errors.DuplicateDatabase:
            print(f"ℹ️  Database {db_name} already exists")
        
        # Grant privileges
        cursor.execute(f"GRANT ALL PRIVILEGES ON DATABASE {db_name} TO {db_user};")
        print(f"✅ Granted privileges to {db_user}")
        
        conn.close()
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection error: {e}")
        print("Please check your PostgreSQL server is running and accessible")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False
    
    return True

def install_extensions():
    """Install required PostgreSQL extensions"""
    
    print("\n🔧 Installing PostgreSQL extensions...")
    
    try:
        # Connect to the MonkHQ database
        db_name = os.environ.get('DB_NAME', 'monkhq')
        db_user = os.environ.get('DB_USER', 'monkhq_user')
        db_password = os.environ.get('DB_PASSWORD', 'monkhq_password')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()
        
        # Install extensions
        extensions = [
            'pg_stat_statements',
            'pg_trgm',
            'unaccent',
            'pgcrypto',
            'btree_gin',
            'btree_gist'
        ]
        
        for ext in extensions:
            try:
                cursor.execute(f"CREATE EXTENSION IF NOT EXISTS {ext};")
                print(f"✅ Installed extension: {ext}")
            except Exception as e:
                print(f"⚠️  Could not install {ext}: {e}")
        
        conn.close()
        print("✅ Extensions installation completed")
        
    except Exception as e:
        print(f"❌ Error installing extensions: {e}")
        return False
    
    return True

def run_django_migrations():
    """Run Django migrations"""
    
    print("\n🔄 Running Django migrations...")
    
    try:
        # Set Django settings module
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monkhq.settings')
        
        # Run migrations
        execute_from_command_line(['manage.py', 'migrate'])
        print("✅ Migrations completed")
        
        # Create superuser (optional)
        create_superuser = input("\nCreate superuser? (y/n): ").lower().strip()
        if create_superuser == 'y':
            execute_from_command_line(['manage.py', 'createsuperuser'])
        
        return True
        
    except Exception as e:
        print(f"❌ Error running migrations: {e}")
        return False

def create_monitoring_functions():
    """Create monitoring functions"""
    
    print("\n📊 Creating monitoring functions...")
    
    try:
        db_name = os.environ.get('DB_NAME', 'monkhq')
        db_user = os.environ.get('DB_USER', 'monkhq_user')
        db_password = os.environ.get('DB_PASSWORD', 'monkhq_password')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()
        
        # Create monitoring functions
        monitoring_functions = """
        -- Function to get database size
        CREATE OR REPLACE FUNCTION get_database_size() 
        RETURNS TEXT AS $$
        BEGIN
            RETURN pg_size_pretty(pg_database_size(current_database()));
        END;
        $$ LANGUAGE plpgsql;

        -- Function to get connection info
        CREATE OR REPLACE FUNCTION get_connection_info()
        RETURNS TABLE(state TEXT, count BIGINT) AS $$
        BEGIN
            RETURN QUERY
            SELECT state, count(*)
            FROM pg_stat_activity
            GROUP BY state;
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
        """
        
        cursor.execute(monitoring_functions)
        conn.commit()
        conn.close()
        
        print("✅ Monitoring functions created")
        return True
        
    except Exception as e:
        print(f"❌ Error creating monitoring functions: {e}")
        return False

def test_connection():
    """Test database connection"""
    
    print("\n🧪 Testing database connection...")
    
    try:
        db_name = os.environ.get('DB_NAME', 'monkhq')
        db_user = os.environ.get('DB_USER', 'monkhq_user')
        db_password = os.environ.get('DB_PASSWORD', 'monkhq_password')
        db_host = os.environ.get('DB_HOST', 'localhost')
        db_port = os.environ.get('DB_PORT', '5432')
        
        conn = psycopg2.connect(
            dbname=db_name,
            user=db_user,
            password=db_password,
            host=db_host,
            port=db_port
        )
        cursor = conn.cursor()
        
        # Test query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        
        print(f"✅ Database connection successful!")
        print(f"📋 PostgreSQL version: {version}")
        
        # Test monitoring function
        cursor.execute("SELECT get_database_size();")
        size = cursor.fetchone()[0]
        print(f"📊 Database size: {size}")
        
        conn.close()
        return True
        
    except Exception as e:
        print(f"❌ Connection test failed: {e}")
        return False

def main():
    """Main setup function"""
    
    print("=" * 50)
    print("🐘 MonkHQ PostgreSQL Setup")
    print("=" * 50)
    
    # Check environment variables
    if not os.environ.get('DB_PASSWORD'):
        print("⚠️  DB_PASSWORD not set. Using default password.")
        print("   Set environment variables for production use:")
        print("   export DB_PASSWORD='your_secure_password'")
        print()
    
    # Run setup steps
    steps = [
        ("Database Setup", setup_database),
        ("Extensions Installation", install_extensions),
        ("Django Migrations", run_django_migrations),
        ("Monitoring Functions", create_monitoring_functions),
        ("Connection Test", test_connection),
    ]
    
    for step_name, step_func in steps:
        print(f"\n📋 {step_name}")
        print("-" * 30)
        
        if not step_func():
            print(f"❌ {step_name} failed!")
            sys.exit(1)
        
        print(f"✅ {step_name} completed!")
    
    print("\n" + "=" * 50)
    print("🎉 PostgreSQL setup completed successfully!")
    print("=" * 50)
    
    print("\n📋 Connection Details:")
    print(f"   Host: {os.environ.get('DB_HOST', 'localhost')}")
    print(f"   Port: {os.environ.get('DB_PORT', '5432')}")
    print(f"   Database: {os.environ.get('DB_NAME', 'monkhq')}")
    print(f"   User: {os.environ.get('DB_USER', 'monkhq_user')}")
    
    print("\n🔧 Next Steps:")
    print("   1. Update .env file with your database credentials")
    print("   2. Run 'python manage.py runserver' to start the application")
    print("   3. Visit http://localhost:8000 to verify everything works")
    print("   4. Use 'python manage.py createsuperuser' to create admin user")
    
    print("\n📊 Monitoring Functions Available:")
    print("   SELECT get_database_size();")
    print("   SELECT * FROM get_connection_info();")
    print("   SELECT * FROM get_table_sizes();")

if __name__ == '__main__':
    main()
