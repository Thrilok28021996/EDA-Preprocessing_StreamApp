import time
import os
import psutil
from django.http import JsonResponse
from django.core.cache import cache
from django.db import connection
from django.conf import settings
import logging

logger = logging.getLogger(__name__)


def health_check(request):
    """Comprehensive health check endpoint for monitoring"""
    
    start_time = time.time()
    health_status = {
        'status': 'healthy',
        'timestamp': time.time(),
        'version': '1.0.0',
        'checks': {}
    }
    
    try:
        # Database health check
        health_status['checks']['database'] = check_database()
        
        # Cache health check
        health_status['checks']['cache'] = check_cache()
        
        # Memory health check
        health_status['checks']['memory'] = check_memory()
        
        # Disk space health check
        health_status['checks']['disk_space'] = check_disk_space()
        
        # Session storage health check
        health_status['checks']['sessions'] = check_sessions()
        
        # Application metrics
        health_status['metrics'] = get_application_metrics()
        
        # Overall health determination
        failed_checks = [name for name, check in health_status['checks'].items() 
                        if check['status'] != 'healthy']
        
        if failed_checks:
            health_status['status'] = 'degraded' if len(failed_checks) < 3 else 'unhealthy'
            health_status['failed_checks'] = failed_checks
        
        health_status['response_time_ms'] = round((time.time() - start_time) * 1000, 2)
        
        # Return appropriate HTTP status
        status_code = 200 if health_status['status'] == 'healthy' else 503
        
        return JsonResponse(health_status, status=status_code)
        
    except Exception as e:
        logger.error(f"Health check failed with error: {str(e)}")
        return JsonResponse({
            'status': 'unhealthy',
            'error': 'Health check system failure',
            'timestamp': time.time(),
            'response_time_ms': round((time.time() - start_time) * 1000, 2)
        }, status=503)


def check_database():
    """Check database connectivity and performance"""
    try:
        start_time = time.time()
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        return {
            'status': 'healthy',
            'response_time_ms': response_time,
            'connection_status': 'connected'
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e),
            'connection_status': 'failed'
        }


def check_cache():
    """Check cache system health"""
    try:
        start_time = time.time()
        test_key = 'health_check_test'
        test_value = str(time.time())
        
        # Test cache write
        cache.set(test_key, test_value, 30)
        
        # Test cache read
        cached_value = cache.get(test_key)
        
        # Test cache delete
        cache.delete(test_key)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if cached_value != test_value:
            return {
                'status': 'unhealthy',
                'error': 'Cache read/write verification failed'
            }
        
        return {
            'status': 'healthy',
            'response_time_ms': response_time,
            'backend': getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'unknown')
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def check_memory():
    """Check system memory usage"""
    try:
        memory = psutil.virtual_memory()
        
        status = 'healthy'
        if memory.percent > 90:
            status = 'critical'
        elif memory.percent > 80:
            status = 'warning'
        
        return {
            'status': status,
            'usage_percent': round(memory.percent, 2),
            'available_gb': round(memory.available / (1024**3), 2),
            'total_gb': round(memory.total / (1024**3), 2)
        }
    except Exception as e:
        return {
            'status': 'unknown',
            'error': str(e)
        }


def check_disk_space():
    """Check available disk space"""
    try:
        # Check disk usage for the Django BASE_DIR
        disk_usage = psutil.disk_usage(settings.BASE_DIR)
        
        usage_percent = (disk_usage.used / disk_usage.total) * 100
        
        status = 'healthy'
        if usage_percent > 95:
            status = 'critical'
        elif usage_percent > 85:
            status = 'warning'
        
        return {
            'status': status,
            'usage_percent': round(usage_percent, 2),
            'free_gb': round(disk_usage.free / (1024**3), 2),
            'total_gb': round(disk_usage.total / (1024**3), 2)
        }
    except Exception as e:
        return {
            'status': 'unknown',
            'error': str(e)
        }


def check_sessions():
    """Check session storage health"""
    try:
        from django.contrib.sessions.backends.cache import SessionStore
        
        start_time = time.time()
        session = SessionStore()
        session['health_check'] = 'test_value'
        session.save()
        
        # Verify session was saved
        session_key = session.session_key
        retrieved_session = SessionStore(session_key)
        
        response_time = round((time.time() - start_time) * 1000, 2)
        
        if retrieved_session.get('health_check') != 'test_value':
            return {
                'status': 'unhealthy',
                'error': 'Session verification failed'
            }
        
        # Clean up test session
        retrieved_session.delete()
        
        return {
            'status': 'healthy',
            'response_time_ms': response_time,
            'engine': settings.SESSION_ENGINE
        }
    except Exception as e:
        return {
            'status': 'unhealthy',
            'error': str(e)
        }


def get_application_metrics():
    """Get application-specific metrics"""
    try:
        # Get process information
        process = psutil.Process(os.getpid())
        
        # Get system load
        load_avg = os.getloadavg() if hasattr(os, 'getloadavg') else [0, 0, 0]
        
        return {
            'process': {
                'cpu_percent': round(process.cpu_percent(), 2),
                'memory_mb': round(process.memory_info().rss / (1024**2), 2),
                'threads': process.num_threads(),
                'uptime_seconds': round(time.time() - process.create_time(), 2)
            },
            'system': {
                'load_average': {
                    '1min': round(load_avg[0], 2),
                    '5min': round(load_avg[1], 2),
                    '15min': round(load_avg[2], 2)
                },
                'cpu_count': psutil.cpu_count(),
                'cpu_percent': round(psutil.cpu_percent(interval=0.1), 2)
            },
            'django': {
                'debug_mode': settings.DEBUG,
                'database_engine': settings.DATABASES['default']['ENGINE'],
                'cache_backend': getattr(settings, 'CACHES', {}).get('default', {}).get('BACKEND', 'unknown'),
                'session_engine': settings.SESSION_ENGINE
            }
        }
    except Exception as e:
        logger.warning(f"Failed to get application metrics: {str(e)}")
        return {
            'error': 'Failed to collect metrics',
            'details': str(e)
        }


def simple_health_check(request):
    """Simple health check for load balancers"""
    try:
        # Quick database check
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
        
        return JsonResponse({'status': 'ok'}, status=200)
    except:
        return JsonResponse({'status': 'error'}, status=503)