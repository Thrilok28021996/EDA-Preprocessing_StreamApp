# Django framework imports
from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

# Standard library imports
import json
import logging
from io import StringIO

# Initialize logger
logger = logging.getLogger(__name__)

# Data processing libraries
import pandas as pd
import numpy as np

# Custom utility functions for data preprocessing
from utils import (
    get_dataframe_from_session,    # Retrieve DataFrame from session
    update_dataframe_in_session,   # Save modified DataFrame to session
    get_basic_info,                # Get basic dataset information
    select_columns,                # Column selection utility
    replace_values,                # Value replacement utility
    filter_dataframe               # Data filtering utility
)


def index(request):
    """Preprocessing main page
    
    Displays the data preprocessing interface where users can:
    - View current dataset information
    - See a sample of the data
    - Access preprocessing operations like column selection, filtering, cleaning
    - Export processed data in various formats
    
    Returns:
        Rendered preprocessing template with dataset information and operation options
    """
    # Ensure user has uploaded a dataset before accessing preprocessing features
    if not request.session.get('df_uploaded', False):
        messages.warning(request, 'Please upload a CSV file in the Home page to get started.')
        return render(request, 'preprocessing/index.html', {'no_data': True})
    
    # Retrieve the current dataset from session storage
    df = get_dataframe_from_session(request)
    if df is None:
        messages.error(request, 'Error loading dataset from session. Please re-upload your CSV file.')
        return render(request, 'preprocessing/index.html', {'no_data': True})
    
    # Extract basic information about the dataset for display
    basic_info = get_basic_info(df)
    
    # Prepare template context with all necessary information
    context = {
        'df_info': basic_info,  # Dataset metadata (shape, types, etc.)
        'numeric_columns': df.select_dtypes(include=[np.number]).columns.tolist(),  # Numerical columns
        'categorical_columns': df.select_dtypes(include=['object', 'category', 'string']).columns.tolist(),  # Text/categorical columns
        'all_columns': df.columns.tolist(),  # Complete column list
        'sample_data': df.head(5).to_dict('records') if not df.empty else []  # Preview of first 5 rows
    }
    
    return render(request, 'preprocessing/index.html', context)


@require_http_methods(["POST"])
def apply_preprocessing(request):
    """Apply preprocessing operations to the dataset
    
    This view handles various data preprocessing operations including:
    - Column selection/removal
    - Value replacement
    - Data filtering
    - Duplicate removal
    - Missing value handling (drop or fill)
    - Data reset to original state
    
    Request format (JSON):
        {
            'operation': 'select_columns',  # Type of preprocessing operation
            'params': {                     # Operation-specific parameters
                'columns': ['col1', 'col2'],
                'method': 'mean',
                'filters': [...]
            }
        }
    
    Returns:
        JSON response with operation result and updated dataset information
    """
    # Only accept POST requests for data modification operations
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests allowed'})
    
    # Retrieve the current dataset from session
    df = get_dataframe_from_session(request)
    if df is None:
        return JsonResponse({'success': False, 'error': 'No dataset found in session'})
    
    try:
        # Parse the preprocessing request
        data = json.loads(request.body)
        operation = data.get('operation')
        params = data.get('params', {})
        
        # Route to appropriate preprocessing function based on operation type
        if operation == 'select_columns':
            # Keep only specified columns in the dataset
            selected_columns = params.get('columns', [])
            if not selected_columns:
                return JsonResponse({'success': False, 'error': 'Please select at least one column'})
            
            df_processed = select_columns(df, selected_columns)
            
        elif operation == 'replace_values':
            # Replace specific values in a column with new values
            column = params.get('column')
            old_value = params.get('old_value')
            new_value = params.get('new_value')
            
            # Validate all required parameters are provided
            if not all([column, old_value is not None, new_value is not None]):
                return JsonResponse({'success': False, 'error': 'Column, old value, and new value are required'})
            
            # Ensure the specified column exists
            if column not in df.columns:
                return JsonResponse({'success': False, 'error': f'Column "{column}" not found'})
            
            df_processed = replace_values(df, column, old_value, new_value)
            
        elif operation == 'filter_data':
            # Apply filtering conditions to reduce the dataset
            filters = params.get('filters', [])
            if not filters:
                return JsonResponse({'success': False, 'error': 'No filters specified'})
            
            df_processed = filter_dataframe(df, filters)
            
        elif operation == 'drop_columns':
            # Remove specified columns from the dataset
            columns_to_drop = params.get('columns', [])
            if not columns_to_drop:
                return JsonResponse({'success': False, 'error': 'Please select columns to drop'})
            
            # Validate that all columns to drop actually exist
            missing_cols = [col for col in columns_to_drop if col not in df.columns]
            if missing_cols:
                return JsonResponse({'success': False, 'error': f'Columns not found: {missing_cols}'})
            
            df_processed = df.drop(columns=columns_to_drop)
            
        elif operation == 'drop_duplicates':
            # Remove duplicate rows from the dataset
            df_processed = df.drop_duplicates()
            
        elif operation == 'drop_missing':
            # Remove rows with missing values
            how = params.get('how', 'any')      # 'any': drop if any NaN, 'all': drop if all NaN
            subset = params.get('subset', None)  # Specific columns to check, or None for all columns
            
            # Validate subset columns if specified
            if subset:
                missing_cols = [col for col in subset if col not in df.columns]
                if missing_cols:
                    return JsonResponse({'success': False, 'error': f'Columns not found: {missing_cols}'})
            
            df_processed = df.dropna(how=how, subset=subset)
            
        elif operation == 'fill_missing':
            # Fill missing values using various strategies
            method = params.get('method', 'mean')  # Fill strategy: 'mean', 'median', 'mode', 'forward', 'backward', 'constant'
            columns = params.get('columns', [])
            constant_value = params.get('constant_value', 0)  # Value for constant fill method
            
            if not columns:
                return JsonResponse({'success': False, 'error': 'Please select columns to fill'})
            
            # Validate all specified columns exist
            missing_cols = [col for col in columns if col not in df.columns]
            if missing_cols:
                return JsonResponse({'success': False, 'error': f'Columns not found: {missing_cols}'})
            
            df_processed = df.copy()
            
            # Apply the specified fill method to each column
            for column in columns:
                if method == 'mean' and pd.api.types.is_numeric_dtype(df_processed[column]):
                    # Fill with column mean (numeric columns only)
                    df_processed[column] = df_processed[column].fillna(df_processed[column].mean())
                elif method == 'median' and pd.api.types.is_numeric_dtype(df_processed[column]):
                    # Fill with column median (numeric columns only)
                    df_processed[column] = df_processed[column].fillna(df_processed[column].median())
                elif method == 'mode':
                    # Fill with most frequent value (works for all data types)
                    mode_val = df_processed[column].mode()
                    if not mode_val.empty:
                        df_processed[column] = df_processed[column].fillna(mode_val.iloc[0])
                elif method == 'forward':
                    # Forward fill - use previous non-null value
                    df_processed[column] = df_processed[column].ffill()
                elif method == 'backward':
                    # Backward fill - use next non-null value
                    df_processed[column] = df_processed[column].bfill()
                elif method == 'constant':
                    # Fill with user-specified constant value
                    df_processed[column] = df_processed[column].fillna(constant_value)
                else:
                    return JsonResponse({'success': False, 'error': f'Invalid fill method for column {column}'})
        
        elif operation == 'reset_data':
            # Reset dataset to its original uploaded state
            # SECURITY FIX: Use secure JSON deserialization instead of pickle
            original_data = request.session.get('original_df_data')
            if original_data:
                from security_utils import deserialize_dataframe_from_json
                df_processed = deserialize_dataframe_from_json(original_data)
            else:
                return JsonResponse({'success': False, 'error': 'Original data not found'})
        
        else:
            return JsonResponse({'success': False, 'error': f'Unknown operation: {operation}'})
        
        # Save the processed DataFrame back to session storage
        success = update_dataframe_in_session(request, df_processed)
        if not success:
            return JsonResponse({'success': False, 'error': 'Failed to update dataset in session'})
        
        # Generate updated dataset information for the response
        new_info = get_basic_info(df_processed)
        
        # Helper function to convert NumPy/Pandas types to JSON-serializable Python types
        def convert_numpy_types(obj):
            """Recursively convert NumPy and Pandas types to native Python types for JSON serialization"""
            if isinstance(obj, dict):
                return {key: convert_numpy_types(value) for key, value in obj.items()}
            elif isinstance(obj, list):
                return [convert_numpy_types(item) for item in obj]
            elif isinstance(obj, (np.integer, np.floating)):
                return obj.item()  # Convert NumPy scalars to Python scalars
            elif isinstance(obj, np.ndarray):
                return obj.tolist()  # Convert NumPy arrays to Python lists
            elif hasattr(obj, 'dtype'):  # Pandas Series or other pandas objects
                return obj.tolist() if hasattr(obj, 'tolist') else str(obj)
            else:
                return obj
        
        # Prepare updated sample data for preview (first 5 rows)
        sample_data = df_processed.head(5).to_dict('records') if not df_processed.empty else []
        
        # Ensure sample data contains only JSON-serializable types
        if sample_data:
            for record in sample_data:
                for key, value in record.items():
                    if isinstance(value, (np.integer, np.floating)):
                        record[key] = value.item()  # Convert NumPy numbers to Python numbers
                    elif pd.isna(value):
                        record[key] = None  # Convert NaN to None for JSON
        
        # Return comprehensive success response with updated dataset information
        return JsonResponse({
            'success': True, 
            'message': f'Operation "{operation}" applied successfully',
            'new_shape': [int(df_processed.shape[0]), int(df_processed.shape[1])],  # Updated dimensions
            'new_info': convert_numpy_types(new_info),   # Converted dataset metadata
            'sample_data': sample_data,                  # Preview of processed data
            'columns': df_processed.columns.tolist()     # Updated column list
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


def export_data(request, format='csv'):
    """Export processed data"""
    # Get DataFrame from session
    df = get_dataframe_from_session(request)
    if df is None:
        # CONSISTENCY FIX: Redirect to home when no data found (matching test expectations)
        messages.error(request, 'No dataset found. Please upload a CSV file first.')
        return redirect('home:index')
    
    
    try:
        if format.lower() == 'csv':
            # Create CSV response
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="processed_data.csv"'
            df.to_csv(response, index=False)
            return response
        
        elif format.lower() == 'json':
            # Create JSON response
            response = HttpResponse(content_type='application/json')
            response['Content-Disposition'] = f'attachment; filename="processed_data.json"'
            df.to_json(response, orient='records', indent=2)
            return response
        
        elif format.lower() == 'excel':
            # Create Excel response
            from io import BytesIO
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            
            response = HttpResponse(
                output.getvalue(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="processed_data.xlsx"'
            return response
        
        else:
            return JsonResponse({'success': False, 'error': f'Unsupported format: {format}'})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def get_column_values(request):
    """Get unique values for a specific column"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests allowed'})
    
    df = get_dataframe_from_session(request)
    if df is None:
        return JsonResponse({'success': False, 'error': 'No dataset found in session'})
    
    try:
        data = json.loads(request.body)
        column = data.get('column')
        
        if not column or column not in df.columns:
            return JsonResponse({'success': False, 'error': 'Valid column name required'})
        
        # Get unique values (limit to 100 for performance)
        unique_values = df[column].dropna().unique()
        if len(unique_values) > 100:
            unique_values = unique_values[:100]
        
        # Convert to list (handle different data types)
        unique_list = []
        for val in unique_values:
            if pd.isna(val):
                continue
            elif isinstance(val, (np.integer, np.floating)):
                unique_list.append(float(val))
            else:
                unique_list.append(str(val))
        
        return JsonResponse({
            'success': True, 
            'values': sorted(unique_list),
            'total_unique': int(df[column].nunique()),
            'has_more': len(unique_values) == 100
        })
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def preview_operation(request):
    """Preview the result of a preprocessing operation without applying it"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests allowed'})
    
    df = get_dataframe_from_session(request)
    if df is None:
        return JsonResponse({'success': False, 'error': 'No dataset found in session'})
    
    try:
        data = json.loads(request.body)
        operation = data.get('operation')
        params = data.get('params', {})
        
        # Apply operation to a copy
        df_preview = df.copy()
        
        if operation == 'select_columns':
            selected_columns = params.get('columns', [])
            df_preview = select_columns(df_preview, selected_columns)
        elif operation == 'drop_duplicates':
            df_preview = df_preview.drop_duplicates()
        elif operation == 'drop_missing':
            how = params.get('how', 'any')
            subset = params.get('subset', None)
            df_preview = df_preview.dropna(how=how, subset=subset)
        # Add more operations as needed
        
        # Get preview info
        preview_info = {
            'original_shape': [int(df.shape[0]), int(df.shape[1])],
            'new_shape': [int(df_preview.shape[0]), int(df_preview.shape[1])],
            'rows_affected': int(df.shape[0] - df_preview.shape[0]),
            'columns_affected': int(df.shape[1] - df_preview.shape[1]),
            'sample_data': df_preview.head(5).to_dict('records') if not df_preview.empty else []
        }
        
        # Convert sample_data NumPy types to Python types
        if preview_info['sample_data']:
            for record in preview_info['sample_data']:
                for key, value in record.items():
                    if isinstance(value, (np.integer, np.floating)):
                        record[key] = value.item()
                    elif pd.isna(value):
                        record[key] = None
        
        return JsonResponse({'success': True, 'preview': preview_info})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})
