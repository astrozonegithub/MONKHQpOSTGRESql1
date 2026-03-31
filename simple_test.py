#!/usr/bin/env python3
"""
Simple test to verify DATABASE_URL parsing
"""

import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
print("Full DATABASE_URL:")
print(DATABASE_URL)
print("\nLength:", len(DATABASE_URL))

# Check if the URL is complete
if "ep-tiny-field-an0w3uqj-pooler.c-6.us-east-1.aws.neon.tech" in DATABASE_URL:
    print("\n✅ Full hostname found in DATABASE_URL")
else:
    print("\n❌ Hostname is truncated in DATABASE_URL")

# Try to connect using Django's database settings
try:
    import django
    from django.conf import settings
    
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monkhq.settings')
    django.setup()
    
    from django.db import connection
    
    print("\n🔌 Testing Django database connection...")
    with connection.cursor() as cursor:
        cursor.execute("SELECT 1;")
        result = cursor.fetchone()
        print(f"✅ Django connection successful: {result[0]}")
        
except Exception as e:
    print(f"\n❌ Django connection failed: {e}")
    print(f"Database config: {settings.DATABASES['default']}")
