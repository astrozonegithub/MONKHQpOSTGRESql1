#!/usr/bin/env python3
"""
Create Django admin user with proper Django setup
"""

import os
import sys
import django
from django.conf import settings
from django.contrib.auth.models import User

def setup_django():
    """Setup Django settings properly"""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monkhq.settings')
    
    # Configure Django settings
    if not settings.configured:
        settings.configure(
            DEBUG=True,
            DATABASES={
                'default': {
                    'ENGINE': 'django.db.backends.postgresql',
                    'NAME': 'neondb',
                    'USER': 'neondb_owner',
                    'PASSWORD': 'npg_OKZUyG06jRIE',
                    'HOST': 'ep-tiny-field-an0w3uqj-pooler.c-6.us-east-1.aws.neon.tech',
                    'PORT': 5432,
                    'OPTIONS': {
                        'sslmode': 'require',
                        'channel_binding': 'require',
                    },
                }
            },
            INSTALLED_APPS=[
                'django.contrib.admin',
                'django.contrib.auth',
                'django.contrib.contenttypes',
                'django.contrib.sessions',
                'django.contrib.messages',
                'django.contrib.staticfiles',
                'core',
            ],
            SECRET_KEY='django-insecure-kkl#m^5yuw9kh3oay!umpoz@m7ct5!5^@%@^t%v9@!vylny26f',
            USE_TZ=True,
        )

def create_admin_user():
    """Create Django admin user"""
    try:
        setup_django()
        
        # Check if user already exists
        if User.objects.filter(username='admin').exists():
            print("✅ Admin user 'admin' already exists")
            return
        
        # Create admin user
        User.objects.create_superuser(
            username='admin',
            email='admin@monkhq.com',
            password='password123',
            first_name='Admin',
            last_name='User'
        )
        
        print("✅ Admin user created successfully!")
        print("   Username: admin")
        print("   Email: admin@monkhq.com")
        print("   Password: password123")
        print("   You can now login to Django admin at http://localhost:8000/admin/")
        
    except Exception as e:
        print(f"❌ Error creating admin user: {e}")

if __name__ == '__main__':
    create_admin_user()
