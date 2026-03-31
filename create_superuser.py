#!/usr/bin/env python3
"""
Create Django superuser for MonkHQ
"""

import os
import django
from django.contrib.auth.models import User

def create_superuser():
    """Create Django superuser"""
    
    # Set Django settings
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monkhq.settings')
    django.setup()
    
    # Check if superuser already exists
    if User.objects.filter(username='admin').exists():
        print("✅ Superuser 'admin' already exists")
        return
    
    # Create superuser
    try:
        User.objects.create_superuser(
            username='admin',
            email='admin@monkhq.com',
            password='password123',
            first_name='Admin',
            last_name='User'
        )
        print("✅ Superuser 'admin' created successfully")
        print("   Username: admin")
        print("   Email: admin@monkhq.com")
        print("   Password: password123")
        print("   You can now login to Django admin at http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"❌ Error creating superuser: {e}")

if __name__ == '__main__':
    create_superuser()
