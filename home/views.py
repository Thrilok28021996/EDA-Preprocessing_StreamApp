"""
Home Application Views

This module handles the main landing page and file upload functionality
for the EDA application. It provides:
- User information display
- CSV file upload with validation and optimization
- Session management for DataFrame storage
- Memory usage monitoring and warnings
- Data type optimization for efficiency

Key features:
- Secure file upload with size and type validation
- Automatic data type optimization for memory efficiency
- Session-based DataFrame storage with backup
- Memory usage monitoring and user warnings
- Error handling with user-friendly messages
"""

# Django framework imports
from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.contrib import messages
from django.conf import settings

# Data processing libraries
import pandas as pd
import numpy as np

# System and utility imports
import os
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Custom utility functions
from utils import (
    process_uploaded_file,        # Optimized CSV file processing
    update_dataframe_in_session,  # Session storage management
    get_memory_usage_info         # Memory usage analysis
)

# SECURITY FIX #5 & #8: Import secure validation utilities
from security_utils import (
    validate_uploaded_file,       # Comprehensive file validation
    log_security_event,           # Security event logging
    serialize_dataframe_to_json,  # Secure serialization
    rate_limit                    # Rate limiting decorator
)


def index(request):
    """Home page with file upload functionality
    
    Displays the main landing page of the EDA application with:
    - Developer/author information
    - File upload interface for CSV files
    - Current session status (if any dataset is loaded)
    
    Returns:
        Rendered home page template with author information context
    """
    # Author/developer information displayed on the home page
    context = {
        'info': {
            'Name': 'Thrilok',
            'Full_Name': 'Thrilok E',
            'Email': 'thriloke96@gmail.com',
            'Intro': 'A Data Science Engineer who likes to explore new technology.',
            'About': (
                "Hey there, I'm Thrilok! I'm passionate about sharing my technical "
                "and data knowledge. My expertise covers a wide range of topics, "
                "from AI/ML and Data Science."
            ),
            'Github': 'https://github.com/Thrilok28021996',
            'City': 'AndhraPradesh, India',
        }
    }
    return render(request, 'home/index.html', context)


@rate_limit(limit=10, window=60)  # SECURITY FIX #10: Rate limiting - 10 uploads per minute
def upload_csv(request):
    """Handle CSV file upload with validation and optimization

    This view processes CSV file uploads with comprehensive validation,
    memory optimization, and session storage. Features include:
    - SECURITY: Comprehensive file validation (MIME type, content, malicious patterns)
    - SECURITY: Rate limiting to prevent abuse
    - SECURITY: Security event logging
    - File type and size validation
    - Memory usage monitoring and warnings
    - Automatic data type optimization
    - Session storage with compression support
    - Original data backup for reset functionality

    Request handling:
    - POST with 'clear_session': Clears current session data
    - POST with 'csv_file': Processes uploaded CSV file

    Returns:
        Redirect to home page with appropriate success/error messages
    """
    if request.method == 'POST':
        # Handle session clearing request
        if request.POST.get('clear_session'):
            clear_session_data(request)
            messages.info(request, 'Session cleared. You can now upload a new file.')
            log_security_event('session_cleared', request)
            return redirect('home:index')

        # Validate that a file was actually uploaded
        if 'csv_file' not in request.FILES:
            messages.error(request, 'No file selected. Please choose a CSV file.')
            return redirect('home:index')

        csv_file = request.FILES['csv_file']

        # SECURITY FIX #8: Comprehensive file upload validation
        # This replaces the simple extension check with full validation
        is_valid, error_message = validate_uploaded_file(
            csv_file,
            allowed_extensions=['csv'],
            max_size_mb=10
        )

        if not is_valid:
            messages.error(request, error_message)
            log_security_event('file_upload_rejected', request, {
                'filename': csv_file.name,
                'size': csv_file.size,
                'reason': error_message
            })
            return redirect('home:index')

        try:
            # Log successful file upload attempt
            log_security_event('file_upload_started', request, {
                'filename': csv_file.name,
                'size': csv_file.size
            })

            # Process the uploaded CSV file with memory optimization
            df = process_uploaded_file(csv_file)
            
            # Validate that the file contains actual data
            if df is None or df.empty:
                messages.error(request, 'The uploaded CSV file is empty or invalid.')
                return redirect('home:index')
            
            # Analyze memory usage and warn users about large datasets
            memory_info = get_memory_usage_info(df)
            memory_usage_mb = memory_info['total_memory_mb']
            
            # Warn users about potentially slow operations with large datasets
            if memory_usage_mb > 50:  # 50MB threshold for performance warnings
                messages.warning(
                    request,
                    f'Large dataset detected ({memory_usage_mb:.1f}MB in memory). '
                    'Some operations may be slower. Consider filtering data if performance issues occur.'
                )
            
            # Store the DataFrame in session with compression if needed
            success = update_dataframe_in_session(request, df)
            
            if not success:
                messages.error(request, 'Failed to store dataset in session. Please try with a smaller file.')
                return redirect('home:index')
            
            # Store metadata about the uploaded file for reference
            request.session['df_uploaded'] = True
            request.session['df_filename'] = csv_file.name
            # CONSISTENCY FIX: Ensure df_shape is stored as list of Python ints, not tuple
            request.session['df_shape'] = [int(df.shape[0]), int(df.shape[1])]

            # Convert memory info to JSON-serializable format for session storage
            serializable_memory_info = {
                'total_memory_mb': float(memory_info['total_memory_mb']),
                'shape': [int(memory_info['shape'][0]), int(memory_info['shape'][1])],  # List, not tuple
                'column_memory': {k: float(v) for k, v in memory_info['column_memory'].items()},
                'dtype_distribution': {str(k): int(v) for k, v in memory_info['dtype_distribution'].items()}
            }
            request.session['df_memory_info'] = serializable_memory_info
            
            # SECURITY FIX #4: Create backup using secure JSON serialization
            # (not pickle which is vulnerable to code injection)
            try:
                original_df_serialized = serialize_dataframe_to_json(df)
                request.session['original_df_data'] = original_df_serialized
            except Exception as e:
                logger.warning(f"Could not create original DataFrame backup: {e}")
            
            messages.success(
                request, 
                f'CSV file "{csv_file.name}" uploaded successfully! '
                f'Shape: {df.shape[0]:,} rows × {df.shape[1]} columns '
                f'(Memory: {memory_usage_mb:.1f}MB)'
            )
            
        except MemoryError:
            messages.error(
                request, 
                'File is too large to process. Please try with a smaller file or contact administrator.'
            )
            return redirect('home:index')
        except Exception as e:
            messages.error(request, f'Error reading CSV file: {str(e)}')
            return redirect('home:index')
    
    return redirect('home:index')


# SECURITY FIX #4: Legacy pickle functions removed
# These functions have been moved to utils.py with secure JSON serialization
# No longer using pickle.loads/dumps to prevent arbitrary code execution


def clear_session_data(request):
    """Clear DataFrame and related data from session
    
    Removes all DataFrame-related data from the Django session,
    allowing users to start fresh with a new dataset.
    
    Args:
        request: Django HTTP request object with session to clear
    
    Note:
        This ensures complete cleanup of all DataFrame-related session data
        including the original backup and memory usage information.
    """
    # List of all session keys related to DataFrame storage
    session_keys = [
        'df_data',           # Serialized DataFrame
        'df_uploaded',       # Upload status flag
        'df_filename',       # Original filename
        'df_shape',          # DataFrame dimensions
        'df_columns',        # Column names
        'original_df_data',  # Backup of original data
        'df_memory_info'     # Memory usage information
    ]
    
    # Remove each key if it exists in the session
    for key in session_keys:
        if key in request.session:
            del request.session[key]
    
    # Mark session as modified to ensure changes are saved
    request.session.modified = True
