#!/usr/bin/env python3
"""
MonkHQ Performance Optimization Script
Optimizes Django settings and static files for production deployment on Koyeb
"""

import os
import subprocess
import sys
from pathlib import Path

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"\n{'='*50}")
    print(f"Running: {description}")
    print(f"Command: {command}")
    print('='*50)
    
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ Success: {result.stdout}")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Error: {e.stderr}")
        return False

def optimize_images():
    """Optimize images in static files"""
    print("\n🖼️  Optimizing images...")
    
    static_dir = Path("static")
    if not static_dir.exists():
        print("No static directory found, skipping image optimization")
        return True
    
    # Optimize PNG files
    png_files = list(static_dir.rglob("*.png"))
    if png_files:
        print(f"Found {len(png_files)} PNG files to optimize")
        for png_file in png_files:
            run_command(f"optipng -o2 {png_file}", f"Optimizing {png_file}")
    
    # Optimize JPEG files
    jpg_files = list(static_dir.rglob("*.jpg")) + list(static_dir.rglob("*.jpeg"))
    if jpg_files:
        print(f"Found {len(jpg_files)} JPEG files to optimize")
        for jpg_file in jpg_files:
            run_command(f"jpegoptim --strip-all {jpg_file}", f"Optimizing {jpg_file}")
    
    return True

def minify_css_js():
    """Minify CSS and JavaScript files"""
    print("\n📦 Minifying CSS and JavaScript...")
    
    # Minify CSS
    css_files = list(Path("static").rglob("*.css"))
    if css_files:
        print(f"Found {len(css_files)} CSS files to minify")
        for css_file in css_files:
            run_command(f"cleancss -o {css_file} {css_file}", f"Minifying {css_file}")
    
    # Minify JS
    js_files = list(Path("static").rglob("*.js"))
    if js_files:
        print(f"Found {len(js_files)} JavaScript files to minify")
        for js_file in js_files:
            run_command(f"terser {js_file} -o {js_file} --compress --mangle", f"Minifying {js_file}")
    
    return True

def collect_static():
    """Collect and compress static files"""
    print("\n🗂️  Collecting static files...")
    
    commands = [
        "python manage.py collectstatic --noinput --clear",
        "python manage.py compress --force",
    ]
    
    for cmd in commands:
        if not run_command(cmd, "Static file collection/compression"):
            return False
    
    return True

def optimize_database():
    """Optimize database settings"""
    print("\n🗄️  Optimizing database...")
    
    commands = [
        "python manage.py migrate --noinput",
        "python manage.py createcachetable",
        "python manage.py check --deploy",
    ]
    
    for cmd in commands:
        if not run_command(cmd, "Database optimization"):
            return False
    
    return True

def create_superuser_if_needed():
    """Create superuser if it doesn't exist"""
    print("\n👤 Checking superuser...")
    
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@monkhq.com')
    
    # Check if superuser exists
    check_cmd = f"python manage.py shell -c \"from django.contrib.auth.models import User; print(User.objects.filter(username='{username}').exists())\""
    
    try:
        result = subprocess.run(check_cmd, shell=True, capture_output=True, text=True)
        if "True" in result.stdout:
            print("✅ Superuser already exists")
            return True
    except:
        pass
    
    # Create superuser
    if os.environ.get('DJANGO_CREATE_SUPERUSER') == 'True':
        create_cmd = f"python manage.py createsuperuser --noinput --username {username} --email {email}"
        return run_command(create_cmd, "Creating superuser")
    
    return True

def run_performance_tests():
    """Run basic performance tests"""
    print("\n⚡ Running performance tests...")
    
    commands = [
        "python manage.py test --verbosity=2",
        "python manage.py check --deploy",
    ]
    
    for cmd in commands:
        if not run_command(cmd, "Performance test"):
            return False
    
    return True

def generate_deployment_info():
    """Generate deployment information"""
    print("\n📋 Generating deployment info...")
    
    info = {
        'timestamp': subprocess.run('date', shell=True, capture_output=True, text=True).stdout.strip(),
        'git_commit': subprocess.run('git rev-parse HEAD', shell=True, capture_output=True, text=True).stdout.strip(),
        'git_branch': subprocess.run('git rev-parse --abbrev-ref HEAD', shell=True, capture_output=True, text=True).stdout.strip(),
        'python_version': sys.version,
        'django_version': subprocess.run('python -c \"import django; print(django.get_version())\"', shell=True, capture_output=True, text=True).stdout.strip(),
    }
    
    with open('deployment_info.json', 'w') as f:
        import json
        json.dump(info, f, indent=2)
    
    print("✅ Deployment info saved to deployment_info.json")
    return True

def main():
    """Main optimization function"""
    print("🚀 MonkHQ Koyeb Optimization Script")
    print("=" * 50)
    
    # Set environment variables
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'monkhq.settings_production')
    
    optimizations = [
        ("Database Optimization", optimize_database),
        ("Static File Collection", collect_static),
        ("Image Optimization", optimize_images),
        ("CSS/JS Minification", minify_css_js),
        ("Superuser Setup", create_superuser_if_needed),
        ("Performance Tests", run_performance_tests),
        ("Deployment Info", generate_deployment_info),
    ]
    
    failed_steps = []
    
    for name, func in optimizations:
        try:
            if not func():
                failed_steps.append(name)
        except Exception as e:
            print(f"❌ {name} failed: {e}")
            failed_steps.append(name)
    
    print("\n" + "="*50)
    if failed_steps:
        print(f"❌ Optimization completed with {len(failed_steps)} failed steps:")
        for step in failed_steps:
            print(f"   - {step}")
        return 1
    else:
        print("✅ All optimizations completed successfully!")
        print("🎉 MonkHQ is ready for Koyeb deployment!")
        return 0

if __name__ == "__main__":
    sys.exit(main())
