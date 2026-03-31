#!/bin/bash
set -e

# Ensure logs dir exists
mkdir -p logs

# Load environment variables from .env if present
if [ -f .env ]; then
    export $(grep -v '^#' .env | xargs)
fi

# Wait for DB host/port if provided (common in deployments)
if [ -n "$DB_HOST" ] && [ -n "$DB_PORT" ]; then
  echo "Waiting for database $DB_HOST:$DB_PORT..."
  while ! nc -z "$DB_HOST" "$DB_PORT"; do
    sleep 0.5
  done
  echo "Database is ready."
fi

# Run Django migrations and collect static files
echo "Running migrations..."
python manage.py migrate --noinput --settings=monkhq.settings_production

echo "Collecting static files..."
python manage.py collectstatic --noinput --settings=monkhq.settings_production

# Start Gunicorn
echo "Starting Gunicorn..."
exec gunicorn monkhq.wsgi:application \
    --bind 0.0.0.0:${PORT:-8000} \
    --workers 3 \
    --timeout 120 \
    --log-level info

