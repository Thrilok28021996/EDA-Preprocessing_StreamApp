"""
Security Utilities Module

Provides secure alternatives to pickle serialization and implements
various security-related utility functions for the Django EDA application.

Key Features:
- JSON-based DataFrame serialization (secure alternative to pickle)
- File upload validation with MIME type checking
- Input sanitization utilities
- Rate limiting helpers
- Security event logging
"""

import json
import logging
import hashlib
import magic
from datetime import datetime
from functools import wraps

import pandas as pd
import numpy as np
from django.core.exceptions import ValidationError
from django.core.cache import cache


# Configure security logger
security_logger = logging.getLogger('security')


# ============================================================================
# SECURE DATAFRAME SERIALIZATION (Replacing Pickle)
# ============================================================================

def serialize_dataframe_to_json(df):
    """
    Securely serialize a DataFrame to JSON format

    This is a safe alternative to pickle.dumps() that prevents arbitrary
    code execution vulnerabilities.

    Args:
        df (DataFrame): Pandas DataFrame to serialize

    Returns:
        str: JSON string representation of the DataFrame

    Note:
        - Handles NaN, Infinity, and datetime objects
        - Preserves data types through metadata
        - Safe from deserialization attacks
    """
    try:
        # Prepare DataFrame metadata for reconstruction
        metadata = {
            'columns': list(df.columns),
            'index': list(df.index.astype(str)),  # Convert index to string for JSON
            'dtypes': {col: str(dtype) for col, dtype in df.dtypes.items()},
            'shape': df.shape
        }

        # Convert DataFrame to dict with proper handling of special values
        # orient='split' is more efficient and preserves data structure
        data_dict = df.to_dict(orient='split')

        # Handle NaN and Infinity values which are not valid JSON
        # Convert them to None which is valid JSON
        def clean_value(val):
            if pd.isna(val):
                return None
            elif isinstance(val, (np.integer, np.floating)):
                if np.isinf(val):
                    return None
                return val.item()  # Convert numpy types to Python types
            elif isinstance(val, pd.Timestamp):
                return val.isoformat()
            elif isinstance(val, (np.ndarray, list)):
                return [clean_value(v) for v in val]
            return val

        cleaned_data = []
        for row in data_dict['data']:
            cleaned_row = [clean_value(val) for val in row]
            cleaned_data.append(cleaned_row)

        data_dict['data'] = cleaned_data

        # Combine metadata and data
        serialized = {
            'metadata': metadata,
            'data': data_dict
        }

        return json.dumps(serialized)

    except Exception as e:
        security_logger.error(f"DataFrame serialization failed: {e}")
        raise ValueError(f"Failed to serialize DataFrame: {str(e)}")


def deserialize_dataframe_from_json(json_str):
    """
    Securely deserialize a DataFrame from JSON format

    Safe alternative to pickle.loads() that prevents arbitrary code execution.

    Args:
        json_str (str): JSON string containing serialized DataFrame

    Returns:
        DataFrame: Reconstructed pandas DataFrame

    Raises:
        ValueError: If deserialization fails or data is corrupted
    """
    try:
        # Parse JSON string
        serialized = json.loads(json_str)

        # Validate structure
        if not isinstance(serialized, dict) or 'metadata' not in serialized or 'data' not in serialized:
            raise ValueError("Invalid serialized DataFrame structure")

        metadata = serialized['metadata']
        data_dict = serialized['data']

        # Reconstruct DataFrame from dict
        df = pd.DataFrame(
            data=data_dict['data'],
            columns=data_dict['columns']
        )

        # Restore data types based on metadata
        for col, dtype_str in metadata['dtypes'].items():
            if col in df.columns:
                try:
                    # Handle different dtype categories
                    if 'int' in dtype_str:
                        df[col] = pd.to_numeric(df[col], errors='coerce').astype('Int64')
                    elif 'float' in dtype_str:
                        df[col] = pd.to_numeric(df[col], errors='coerce')
                    elif 'datetime' in dtype_str:
                        df[col] = pd.to_datetime(df[col], errors='coerce')
                    elif 'bool' in dtype_str:
                        df[col] = df[col].astype('boolean')
                    elif 'category' in dtype_str:
                        df[col] = df[col].astype('category')
                    # object/string types remain as-is
                except Exception as e:
                    security_logger.warning(f"Could not restore dtype for column {col}: {e}")

        return df

    except json.JSONDecodeError as e:
        security_logger.error(f"JSON deserialization failed: {e}")
        raise ValueError("Invalid JSON data")
    except Exception as e:
        security_logger.error(f"DataFrame deserialization failed: {e}")
        raise ValueError(f"Failed to deserialize DataFrame: {str(e)}")


# ============================================================================
# FILE UPLOAD VALIDATION
# ============================================================================

def validate_uploaded_file(uploaded_file, allowed_extensions=None, max_size_mb=10):
    """
    Comprehensive file upload validation

    Validates:
    - File extension
    - MIME type
    - File size
    - Content validation
    - Malicious content detection

    Args:
        uploaded_file: Django UploadedFile object
        allowed_extensions (list): List of allowed file extensions (default: ['csv'])
        max_size_mb (int): Maximum file size in megabytes (default: 10)

    Returns:
        tuple: (is_valid, error_message)

    Security Features:
    - MIME type verification to prevent file type spoofing
    - Size limit enforcement
    - Extension whitelist
    - Basic malicious content detection
    """
    if allowed_extensions is None:
        allowed_extensions = ['csv']

    # Check if file exists
    if not uploaded_file:
        return False, "No file provided"

    # 1. Check file extension
    filename = uploaded_file.name.lower()
    file_ext = filename.split('.')[-1] if '.' in filename else ''

    if file_ext not in allowed_extensions:
        security_logger.warning(f"Invalid file extension attempted: {file_ext}")
        return False, f"Invalid file type. Allowed types: {', '.join(allowed_extensions)}"

    # 2. Check file size
    max_size_bytes = max_size_mb * 1024 * 1024
    if uploaded_file.size > max_size_bytes:
        security_logger.warning(f"File size exceeded: {uploaded_file.size} bytes")
        return False, f"File too large. Maximum size: {max_size_mb}MB"

    # 3. MIME type validation using python-magic
    try:
        # Read first chunk for MIME detection
        uploaded_file.seek(0)
        file_content = uploaded_file.read(8192)  # Read first 8KB
        uploaded_file.seek(0)  # Reset file pointer

        # Detect MIME type
        mime_type = magic.from_buffer(file_content, mime=True)

        # Allowed MIME types for CSV
        allowed_mime_types = [
            'text/csv',
            'text/plain',
            'application/csv',
            'application/vnd.ms-excel',  # Some systems detect CSV as Excel
            'text/x-csv'
        ]

        if mime_type not in allowed_mime_types:
            security_logger.warning(f"Invalid MIME type detected: {mime_type} for file {filename}")
            return False, f"Invalid file content type. Expected CSV file."

    except Exception as e:
        security_logger.error(f"MIME type validation failed: {e}")
        # Continue with other validations if MIME check fails

    # 4. Content validation - check if it's actually parseable as CSV
    try:
        uploaded_file.seek(0)
        # Try to read just the first few lines to validate CSV structure
        sample = uploaded_file.read(10000).decode('utf-8', errors='ignore')
        uploaded_file.seek(0)

        # Basic CSV structure validation
        lines = sample.split('\n')
        if len(lines) < 2:
            return False, "File appears to be empty or invalid CSV format"

        # Check for potentially malicious content
        malicious_patterns = ['<script', '<?php', '<%', 'eval(', 'exec(', '__import__']
        sample_lower = sample.lower()

        for pattern in malicious_patterns:
            if pattern in sample_lower:
                security_logger.error(f"Malicious pattern detected in upload: {pattern}")
                return False, "File contains potentially malicious content"

    except UnicodeDecodeError:
        return False, "File encoding not supported. Please use UTF-8 encoded CSV"
    except Exception as e:
        security_logger.error(f"Content validation failed: {e}")
        return False, f"File validation failed: {str(e)}"

    # All validations passed
    return True, "File is valid"


# ============================================================================
# INPUT SANITIZATION
# ============================================================================

def sanitize_email(email):
    """
    Sanitize and validate email input

    Prevents:
    - Email header injection
    - XSS attacks
    - Invalid email formats

    Args:
        email (str): Email address to sanitize

    Returns:
        str: Sanitized email or raises ValidationError
    """
    from django.core.validators import validate_email as django_validate_email

    if not email:
        raise ValidationError("Email is required")

    email = email.strip().lower()

    # Check for header injection attempts
    dangerous_chars = ['\n', '\r', '\0', '%0a', '%0d']
    for char in dangerous_chars:
        if char in email.lower():
            security_logger.warning(f"Email injection attempt detected: {email}")
            raise ValidationError("Invalid email format")

    # Use Django's email validator
    try:
        django_validate_email(email)
    except ValidationError:
        raise ValidationError("Invalid email address")

    # Additional checks
    if len(email) > 254:  # RFC 5321
        raise ValidationError("Email address too long")

    return email


def sanitize_text_input(text, max_length=5000, allow_html=False):
    """
    Sanitize text input to prevent XSS and injection attacks

    Args:
        text (str): Input text to sanitize
        max_length (int): Maximum allowed length
        allow_html (bool): Whether to allow HTML tags

    Returns:
        str: Sanitized text
    """
    if not text:
        return ""

    text = text.strip()

    # Length check
    if len(text) > max_length:
        text = text[:max_length]

    if not allow_html:
        # Remove HTML tags and dangerous characters
        import html
        text = html.escape(text)

    # Remove null bytes
    text = text.replace('\x00', '')

    return text


# ============================================================================
# RATE LIMITING
# ============================================================================

def check_rate_limit(identifier, limit=10, window=60):
    """
    Check if rate limit is exceeded

    Args:
        identifier (str): Unique identifier (IP address, user ID, etc.)
        limit (int): Maximum number of requests
        window (int): Time window in seconds

    Returns:
        tuple: (is_allowed, remaining_requests)
    """
    cache_key = f"rate_limit:{identifier}"

    # Get current count
    current = cache.get(cache_key, 0)

    if current >= limit:
        security_logger.warning(f"Rate limit exceeded for {identifier}")
        return False, 0

    # Increment counter
    cache.set(cache_key, current + 1, window)

    return True, limit - current - 1


def rate_limit(limit=10, window=60, key_func=None):
    """
    Rate limiting decorator

    Args:
        limit (int): Maximum number of requests
        window (int): Time window in seconds
        key_func (callable): Function to generate unique identifier from request

    Usage:
        @rate_limit(limit=5, window=60)
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Generate identifier
            if key_func:
                identifier = key_func(request)
            else:
                identifier = get_client_ip(request)

            # Check rate limit
            is_allowed, remaining = check_rate_limit(
                f"{view_func.__name__}:{identifier}",
                limit=limit,
                window=window
            )

            if not is_allowed:
                from django.http import JsonResponse
                security_logger.warning(
                    f"Rate limit exceeded for {identifier} on {view_func.__name__}"
                )
                return JsonResponse({
                    'error': 'Rate limit exceeded. Please try again later.',
                    'retry_after': window
                }, status=429)

            return view_func(request, *args, **kwargs)

        return wrapper
    return decorator


# ============================================================================
# SECURITY EVENT LOGGING
# ============================================================================

def log_security_event(event_type, request, details=None):
    """
    Log security-related events

    Args:
        event_type (str): Type of security event
        request: Django request object
        details (dict): Additional event details
    """
    event_data = {
        'timestamp': datetime.now().isoformat(),
        'event_type': event_type,
        'ip_address': get_client_ip(request),
        'user_agent': request.META.get('HTTP_USER_AGENT', ''),
        'path': request.path,
        'method': request.method,
        'user': str(request.user) if hasattr(request, 'user') else 'anonymous'
    }

    if details:
        event_data.update(details)

    security_logger.info(f"Security event: {event_type}", extra=event_data)


# ============================================================================
# UTILITY FUNCTIONS
# ============================================================================

def get_client_ip(request):
    """
    Get client IP address from request

    Args:
        request: Django request object

    Returns:
        str: Client IP address
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    return ip


def generate_secure_token():
    """
    Generate a secure random token

    Returns:
        str: Secure random token (hex string)
    """
    import secrets
    return secrets.token_hex(32)


def hash_sensitive_data(data):
    """
    Hash sensitive data for storage

    Args:
        data (str): Data to hash

    Returns:
        str: SHA-256 hash of the data
    """
    return hashlib.sha256(data.encode()).hexdigest()


# ============================================================================
# SESSION SIZE MONITORING
# ============================================================================

def check_session_size(request, max_size_mb=5):
    """
    Check if session data size exceeds limit

    Args:
        request: Django request object
        max_size_mb (int): Maximum session size in MB

    Returns:
        tuple: (is_within_limit, current_size_mb)
    """
    import sys

    # Calculate session data size
    session_size = sys.getsizeof(str(request.session.items()))
    session_size_mb = session_size / (1024 * 1024)

    if session_size_mb > max_size_mb:
        security_logger.warning(
            f"Large session detected: {session_size_mb:.2f}MB for session {request.session.session_key}"
        )
        return False, session_size_mb

    return True, session_size_mb
