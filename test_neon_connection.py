#!/usr/bin/env python3
"""
Test Neon PostgreSQL Connection for MonkHQ
Verifies DATABASE_URL parsing and database connectivity
"""

import os
import sys
import psycopg2
from urllib.parse import urlparse, parse_qsl
from dotenv import load_dotenv

def test_database_url_parsing():
    """Test DATABASE_URL parsing"""
    print("🔍 Testing DATABASE_URL parsing...")
    
    # Load environment
    load_dotenv()
    DATABASE_URL = os.getenv("DATABASE_URL")
    
    if not DATABASE_URL:
        print("❌ DATABASE_URL not found in environment")
        print("   Please set DATABASE_URL in your .env file")
        return False
    
    print(f"📋 DATABASE_URL: {DATABASE_URL}")
    
    try:
        # Parse URL
        tmpPostgres = urlparse(DATABASE_URL)
        
        # Handle case where port is in hostname (common with Neon)
        if tmpPostgres.port is None and ':' in tmpPostgres.hostname:
            host_parts = tmpPostgres.hostname.split(':')
            if len(host_parts) == 2:
                tmpPostgres = tmpPostgres._replace(
                    hostname=host_parts[0],
                    port=int(host_parts[1])
                )
        
        print("✅ URL Parsing Results:")
        print(f"   Scheme: {tmpPostgres.scheme}")
        print(f"   Username: {tmpPostgres.username}")
        print(f"   Password: {'*' * len(tmpPostgres.password) if tmpPostgres.password else 'None'}")
        print(f"   Hostname: {tmpPostgres.hostname}")
        print(f"   Port: {tmpPostgres.port}")
        print(f"   Database: {tmpPostgres.path.replace('/', '')}")
        
        # Parse query parameters
        query_params = dict(parse_qsl(tmpPostgres.query))
        
        # Force SSL mode for Neon if not specified
        if 'sslmode' not in query_params:
            query_params['sslmode'] = 'require'
        
        # Ensure channel binding for Neon
        if 'channel_binding' not in query_params:
            query_params['channel_binding'] = 'require'
        
        print(f"   Query Parameters: {query_params}")
        
        return tmpPostgres, query_params
        
    except Exception as e:
        print(f"❌ URL parsing failed: {e}")
        return None, None

def test_database_connection(parsed_url, query_params):
    """Test actual database connection"""
    print("\n🔌 Testing database connection...")
    
    if not parsed_url:
        return False
    
    try:
        # Connect to database
        conn = psycopg2.connect(
            dbname=parsed_url.path.replace('/', ''),
            user=parsed_url.username,
            password=parsed_url.password,
            host=parsed_url.hostname,
            port=parsed_url.port or 5432,
            options=query_params
        )
        
        cursor = conn.cursor()
        
        # Test basic query
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"✅ Database connection successful!")
        print(f"📋 PostgreSQL version: {version}")
        
        # Test database info
        cursor.execute("SELECT current_database(), current_user, inet_server_addr();")
        db_info = cursor.fetchone()
        print(f"🗄️  Database: {db_info[0]}")
        print(f"👤 User: {db_info[1]}")
        print(f"🌐 Server: {db_info[2]}")
        
        # Test connection options
        cursor.execute("SHOW application_name;")
        app_name = cursor.fetchone()[0]
        print(f"🏷️  Application Name: {app_name}")
        
        # Test SSL status
        cursor.execute("SHOW ssl;")
        ssl_status = cursor.fetchone()[0]
        print(f"🔒 SSL Status: {ssl_status}")
        
        conn.close()
        return True
        
    except psycopg2.OperationalError as e:
        print(f"❌ Connection error: {e}")
        print("   Please check your DATABASE_URL and network connectivity")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_django_settings():
    """Test Django settings configuration"""
    print("\n🐍 Testing Django settings...")
    
    try:
        # Add current directory to Python path
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
        
        # Set Django settings
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monkhq.settings')
        
        import django
        from django.conf import settings
        
        django.setup()
        
        # Test database configuration
        from django.db import connection
        
        print("✅ Django settings loaded successfully")
        print(f"🗄️  Database Engine: {settings.DATABASES['default']['ENGINE']}")
        print(f"🏷️  Application Name: {settings.DATABASES['default']['OPTIONS'].get('application_name', 'None')}")
        
        # Test database connection through Django
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1;")
            result = cursor.fetchone()
            print(f"✅ Django database connection successful!")
            print(f"🔢 Test query result: {result[0]}")
        
        return True
        
    except Exception as e:
        print(f"❌ Django settings error: {e}")
        return False

def create_sample_data():
    """Create sample data to test database functionality"""
    print("\n📝 Testing database operations...")
    
    try:
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monkhq.settings')
        
        import django
        django.setup()
        
        from django.db import connection
        
        # Create test table
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS test_neon_connection (
                    id SERIAL PRIMARY KEY,
                    message TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                );
            """)
            
            # Insert test data
            cursor.execute("""
                INSERT INTO test_neon_connection (message) 
                VALUES ('Neon PostgreSQL connection test - %s')
                RETURNING id, message, created_at;
            """, [connection.vendor])
            
            result = cursor.fetchone()
            print(f"✅ Sample data created:")
            print(f"   ID: {result[0]}")
            print(f"   Message: {result[1]}")
            print(f"   Created At: {result[2]}")
            
            # Clean up
            cursor.execute("DROP TABLE IF EXISTS test_neon_connection;")
            print("✅ Test table cleaned up")
        
        return True
        
    except Exception as e:
        print(f"❌ Database operations error: {e}")
        return False

def main():
    """Main test function"""
    print("=" * 60)
    print("🐘 MonkHQ Neon PostgreSQL Connection Test")
    print("=" * 60)
    
    # Test URL parsing
    parsed_url, query_params = test_database_url_parsing()
    if not parsed_url:
        sys.exit(1)
    
    # Test database connection
    if not test_database_connection(parsed_url, query_params):
        sys.exit(1)
    
    # Test Django settings
    if not test_django_settings():
        sys.exit(1)
    
    # Test database operations
    if not create_sample_data():
        sys.exit(1)
    
    print("\n" + "=" * 60)
    print("🎉 All tests passed! Neon PostgreSQL is working correctly!")
    print("=" * 60)
    
    print("\n📋 Next Steps:")
    print("   1. Run 'python manage.py migrate' to set up database tables")
    print("   2. Run 'python manage.py createsuperuser' to create admin user")
    print("   3. Run 'python manage.py runserver' to start the application")
    print("   4. Visit http://localhost:8000 to access MonkHQ")
    
    print("\n🔧 Configuration Summary:")
    print(f"   DATABASE_URL: {os.getenv('DATABASE_URL', 'Not set')}")
    print(f"   Django Settings: monkhq.settings")
    print(f"   Database Engine: django.db.backends.postgresql")

if __name__ == '__main__':
    main()
