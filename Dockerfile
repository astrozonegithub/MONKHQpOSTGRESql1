# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        gcc \
        libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . .

# Create necessary directories
RUN mkdir -p staticfiles media logs

# Collect static files
RUN python manage.py collectstatic --noinput || true

# Run migrations (optional - can be done in build command)
# RUN python manage.py migrate --noinput || true

# Expose port
EXPOSE 8000

# Use gunicorn to run the application
CMD gunicorn monkhq.wsgi:application --bind 0.0.0.0:8000 --workers 2 --timeout 120
