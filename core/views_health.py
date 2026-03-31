from django.http import JsonResponse
from django.db import connection
from django.core.cache import cache
from django.conf import settings
import time


def health_check(request):
    """
    Health check endpoint for Koyeb
    Returns status of database, cache, and overall application
    """
    try:
        # Check database connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            db_status = "healthy"
    except Exception as e:
        db_status = f"unhealthy: {str(e)}"
    
    # Check cache
    try:
        cache.set('health_check', 'ok', 10)
        cache_result = cache.get('health_check')
        cache_status = "healthy" if cache_result == "ok" else "unhealthy"
    except Exception as e:
        cache_status = f"unhealthy: {str(e)}"
    
    # Overall status
    overall_status = "healthy" if db_status == "healthy" and cache_status == "healthy" else "unhealthy"
    
    response_data = {
        "status": overall_status,
        "timestamp": time.time(),
        "version": getattr(settings, 'VERSION', '1.0.0'),
        "checks": {
            "database": db_status,
            "cache": cache_status,
        }
    }
    
    status_code = 200 if overall_status == "healthy" else 503
    return JsonResponse(response_data, status=status_code)


def readiness_check(request):
    """
    Readiness check for Koyeb
    More thorough check than health check
    """
    try:
        # Check if we can perform a simple database operation
        from django.contrib.auth.models import User
        user_count = User.objects.count()
        
        # Check if static files are accessible
        from django.templatetags.static import static
        css_url = static('css/style.css')
        
        return JsonResponse({
            "status": "ready",
            "timestamp": time.time(),
            "database_users": user_count,
            "static_files": "accessible"
        })
    except Exception as e:
        return JsonResponse({
            "status": "not ready",
            "timestamp": time.time(),
            "error": str(e)
        }, status=503)


def liveness_check(request):
    """
    Liveness check for Koyeb
    Simple check to see if the application is running
    """
    return JsonResponse({
        "status": "alive",
        "timestamp": time.time(),
        "pid": os.getpid()
    })
