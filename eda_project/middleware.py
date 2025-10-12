import logging
import traceback
from django.http import JsonResponse, HttpResponseServerError
from django.shortcuts import render
from django.conf import settings
from django.contrib import messages
from django.utils.deprecation import MiddlewareMixin
import time


logger = logging.getLogger(__name__)


class ErrorHandlingMiddleware(MiddlewareMixin):
    """Comprehensive error handling middleware"""
    
    def process_exception(self, request, exception):
        """Handle exceptions and provide user-friendly error responses"""
        
        # Log the exception
        logger.error(
            f"Unhandled exception in {request.path}: {str(exception)}",
            extra={
                'request_path': request.path,
                'request_method': request.method,
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'remote_addr': self.get_client_ip(request),
                'exception_type': type(exception).__name__,
                'traceback': traceback.format_exc()
            }
        )
        
        # Handle AJAX requests
        if request.headers.get('Content-Type') == 'application/json' or request.path.startswith('/api/'):
            return JsonResponse({
                'success': False,
                'error': 'An unexpected error occurred. Please try again or contact support.',
                'error_code': 'INTERNAL_SERVER_ERROR'
            }, status=500)
        
        # Handle regular requests
        if settings.DEBUG:
            # Let Django handle it in debug mode
            return None
        
        # Production error handling
        context = {
            'error_message': 'An unexpected error occurred. Our team has been notified.',
            'error_code': 'INTERNAL_SERVER_ERROR',
            'support_email': 'thriloke96@gmail.com'
        }
        
        return render(request, 'errors/500.html', context, status=500)
    
    def get_client_ip(self, request):
        """Get client IP address"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class PerformanceMonitoringMiddleware(MiddlewareMixin):
    """Monitor request performance and log slow requests"""
    
    def process_request(self, request):
        request._start_time = time.time()
    
    def process_response(self, request, response):
        if hasattr(request, '_start_time'):
            duration = time.time() - request._start_time
            
            # Log slow requests (> 5 seconds)
            if duration > 5:
                logger.warning(
                    f"Slow request detected: {request.path} took {duration:.2f}s",
                    extra={
                        'request_path': request.path,
                        'request_method': request.method,
                        'duration': duration,
                        'status_code': response.status_code
                    }
                )
            
            # Add performance header for monitoring
            response['X-Response-Time'] = f"{duration:.3f}s"
        
        return response


class SessionValidationMiddleware(MiddlewareMixin):
    """Validate session data integrity

    SECURITY FIX: Replaced pickle validation with secure JSON deserialization
    """

    def process_request(self, request):
        # Check for corrupted DataFrame in session
        if request.session.get('df_uploaded'):
            try:
                from security_utils import deserialize_dataframe_from_json
                df_data = request.session.get('df_data')
                if df_data:
                    # Try to deserialize to check integrity using secure method
                    if request.session.get('df_compressed', False):
                        import gzip
                        import io
                        compressed_data = bytes(df_data)
                        with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                            json_data = f.read().decode('utf-8')
                            deserialize_dataframe_from_json(json_data)
                    else:
                        if isinstance(df_data, (bytes, bytearray)):
                            df_data = df_data.decode('utf-8')
                        deserialize_dataframe_from_json(df_data)
            except Exception as e:
                logger.warning(
                    f"Corrupted session data detected, clearing session: {str(e)}",
                    extra={'session_key': request.session.session_key}
                )
                # Clear corrupted session data
                session_keys = ['df_data', 'df_uploaded', 'df_filename', 'df_shape', 'df_columns', 'original_df_data', 'df_compressed']
                for key in session_keys:
                    if key in request.session:
                        del request.session[key]
                request.session.modified = True

                # Add warning message
                messages.warning(
                    request,
                    'Your session data was corrupted and has been cleared. Please upload your CSV file again.'
                )


class CSVProcessingErrorMiddleware(MiddlewareMixin):
    """Handle CSV processing specific errors"""
    
    def process_exception(self, request, exception):
        """Handle CSV processing exceptions"""
        
        # Handle pandas specific errors
        if 'pandas' in str(type(exception)):
            if 'ParserError' in str(type(exception)):
                error_msg = 'The CSV file format is invalid. Please check your file and try again.'
            elif 'EmptyDataError' in str(type(exception)):
                error_msg = 'The CSV file appears to be empty.'
            elif 'UnicodeDecodeError' in str(type(exception)):
                error_msg = 'The CSV file encoding is not supported. Please save your file as UTF-8.'
            else:
                error_msg = 'Error processing CSV file. Please check the file format and try again.'
            
            logger.warning(
                f"CSV processing error: {str(exception)}",
                extra={
                    'request_path': request.path,
                    'exception_type': type(exception).__name__
                }
            )
            
            # Handle AJAX requests
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': error_msg,
                    'error_code': 'CSV_PROCESSING_ERROR'
                })
            
            # Handle regular requests
            messages.error(request, error_msg)
            return None
        
        # Handle memory errors
        if isinstance(exception, MemoryError):
            error_msg = 'The file is too large to process. Please try with a smaller file.'
            
            logger.error(
                f"Memory error processing request: {request.path}",
                extra={'request_path': request.path}
            )
            
            if request.headers.get('Content-Type') == 'application/json':
                return JsonResponse({
                    'success': False,
                    'error': error_msg,
                    'error_code': 'MEMORY_ERROR'
                })
            
            messages.error(request, error_msg)
            return None
        
        return None


class SecurityMiddleware(MiddlewareMixin):
    """Enhanced security middleware

    SECURITY FIX #13: Content Security Policy
    NOTE: 'unsafe-inline' and 'unsafe-eval' are required for Plotly.js
    interactive charts. This is a known trade-off between functionality
    and strict CSP. Mitigations:
    - Strict CSP for all other resources
    - Only allow trusted CDNs (cdn.plot.ly, cdnjs.cloudflare.com)
    - Regular security monitoring
    """

    def process_response(self, request, response):
        # Add security headers
        if not settings.DEBUG:
            response['X-Content-Type-Options'] = 'nosniff'
            response['X-Frame-Options'] = 'DENY'
            response['X-XSS-Protection'] = '1; mode=block'
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'

            # SECURITY FIX #13: Content Security Policy for EDA app
            # Note: unsafe-inline/unsafe-eval required for Plotly charts
            csp = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdn.plot.ly https://cdnjs.cloudflare.com; "
                "style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com; "
                "img-src 'self' data: https:; "
                "font-src 'self' https://cdnjs.cloudflare.com; "
                "connect-src 'self';"
            )
            response['Content-Security-Policy'] = csp

        return response