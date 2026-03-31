#!/bin/bash
set -e

# Load environment variables from .env if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Collect static files
python manage.py collectstatic --noinput --settings=monkhq.settings_production

# Run migrations
python manage.py migrate --settings=monkhq.settings_production

# Start Gunicorn server
exec gunicorn monkhq.wsgi:application --bind 0.0.0.0:8000#!/bin/bash

# Create logs directory
mkdir -p logs

# Wait for database to be ready (if using PostgreSQL)
echo "Waiting for database..."
while ! nc -z $DB_HOST $DB_PORT; do
  sleep 0.1
done
echo "Database is ready!"

# Run Django migrations
echo "Running migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Create superuser if needed (for initial setup)
if [ "$DJANGO_CREATE_SUPERUSER" = "True" ]; then
  echo "Creating superuser..."
  python manage.py createsuperuser --noinput --username $DJANGO_SUPERUSER_USERNAME --email $DJANGO_SUPERUSER_EMAIL || true
fi

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn monkhq.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 3 \
    --worker-class sync \
    --worker-tmp-dir /dev/shm \
    --timeout 120 \
    --keepalive 5 \
    --max-requests 1000 \
    --max-requests-jitter 100 \
    --access-logfile - \
    --error-logfile - \
    --log-level info
