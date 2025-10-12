"""
Utility functions for DataFrame operations - Django version of original utils.py

This module provides comprehensive utilities for:
- DataFrame session management with compression
- Data preprocessing and cleaning operations
- Performance monitoring and memory optimization
- Statistical analysis and data validation
- Chart generation and data export functionality

Key features:
- Automatic memory optimization for large datasets
- Compressed session storage for efficient memory usage
- Performance monitoring with execution time tracking
- Robust error handling and data type conversions
- Support for various file formats (CSV, JSON, Excel)
"""

# Core data processing libraries
import pandas as pd
import numpy as np

# Data serialization and compression
import gzip
import io

# Performance monitoring
import time
import logging
from functools import wraps
from typing import Dict, Any, Optional, Tuple, Callable

# Security utilities - secure DataFrame serialization
from security_utils import (
    serialize_dataframe_to_json,
    deserialize_dataframe_from_json
)

# Configure logging
logger = logging.getLogger(__name__)


# ============================================================================
# PERFORMANCE MONITORING UTILITIES
# ============================================================================

def performance_monitor(operation_name: str) -> Callable:
    """Decorator to monitor performance of DataFrame operations

    Tracks execution time of data processing functions and logs performance
    metrics for operations that take longer than 1 second. This helps identify
    bottlenecks in data processing workflows.

    Args:
        operation_name (str): Human-readable name for the operation being monitored

    Returns:
        Callable: Decorated function with performance monitoring capabilities

    Usage:
        @performance_monitor("Large File Processing")
        def process_large_file(file_path):
            # Function implementation
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            start_time = time.time()
            try:
                result = func(*args, **kwargs)
                end_time = time.time()
                execution_time = end_time - start_time

                # Log performance metrics for slow operations
                # This threshold can be adjusted based on application requirements
                if execution_time > 1.0:
                    logger.info(f"Performance: {operation_name} took {execution_time:.2f}s")

                return result
            except Exception as e:
                end_time = time.time()
                execution_time = end_time - start_time
                logger.error(f"Performance: {operation_name} failed after {execution_time:.2f}s - {str(e)}")
                raise
        return wrapper
    return decorator


def get_memory_usage_info(df: pd.DataFrame) -> Dict[str, Any]:
    """Get detailed memory usage information for DataFrame

    Provides comprehensive memory analysis including total usage,
    per-column memory consumption, and data type distribution.
    Useful for optimizing memory usage in large datasets.

    Args:
        df (pd.DataFrame): Pandas DataFrame to analyze

    Returns:
        Dict[str, Any]: Memory usage information including:
            - total_memory_mb: Total memory usage in megabytes
            - shape: DataFrame dimensions (rows, columns)
            - column_memory: Memory usage per column in MB
            - dtype_distribution: Count of each data type
    """
    memory_info = {
        'total_memory_mb': df.memory_usage(deep=True).sum() / (1024 * 1024),
        'shape': df.shape,
        'column_memory': {
            col: df[col].memory_usage(deep=True) / (1024 * 1024)
            for col in df.columns
        },
        'dtype_distribution': df.dtypes.value_counts().to_dict()
    }
    return memory_info


# ============================================================================
# SESSION MANAGEMENT UTILITIES
# ============================================================================

def get_dataframe_from_session(request: Any) -> Optional[pd.DataFrame]:
    """Get DataFrame from session storage with secure JSON deserialization

    Retrieves a pandas DataFrame from Django session storage, automatically
    handling both compressed and uncompressed data. This allows for efficient
    storage of large datasets in memory-constrained environments.

    Args:
        request: Django HTTP request object containing session data

    Returns:
        Optional[pd.DataFrame]: The stored DataFrame, or None if not found or error occurred

    Note:
        - Automatically detects and handles compressed vs uncompressed data
        - Uses secure JSON serialization (not pickle) to prevent code injection
        - Gracefully handles errors and returns None on failure

    Security:
        - FIXED: Replaced pickle.loads with secure JSON deserialization
        - Prevents arbitrary code execution attacks
    """
    # Check if user has uploaded a dataset
    if not request.session.get('df_uploaded', False):
        return None

    try:
        df_data = request.session.get('df_data')
        if df_data:
            # Determine if data is stored in compressed format
            if request.session.get('df_compressed', False):
                # Decompress and deserialize the DataFrame
                compressed_data = bytes(df_data)
                with gzip.GzipFile(fileobj=io.BytesIO(compressed_data), mode='rb') as f:
                    json_data = f.read().decode('utf-8')
                    return deserialize_dataframe_from_json(json_data)
            else:
                # Directly deserialize uncompressed data (JSON string)
                if isinstance(df_data, (bytes, bytearray)):
                    df_data = df_data.decode('utf-8')
                return deserialize_dataframe_from_json(df_data)
    except Exception as e:
        logger.error(f"Error loading DataFrame from session: {e}")

    return None


def update_dataframe_in_session(request: Any, df: pd.DataFrame, compress_threshold: int = 1024*1024) -> bool:
    """Update DataFrame in session storage with secure JSON serialization

    Stores a pandas DataFrame in Django session with automatic compression
    for large datasets. Includes memory optimization and metadata storage.

    Args:
        request: Django HTTP request object with session
        df (pd.DataFrame): Pandas DataFrame to store
        compress_threshold (int): Size threshold in bytes for compression (default: 1MB)

    Returns:
        bool: True if successful, False if error occurred

    Features:
        - Automatic memory optimization before storage
        - Intelligent compression (only if it reduces size)
        - Metadata storage for quick access to DataFrame info
        - Error handling with detailed logging

    Security:
        - FIXED: Replaced pickle.dumps with secure JSON serialization
        - Prevents arbitrary code execution attacks
    """
    try:
        # Optimize DataFrame memory usage before storing
        df_optimized = optimize_dataframe_memory(df)

        # Serialize the DataFrame to JSON (secure alternative to pickle)
        df_serialized = serialize_dataframe_to_json(df_optimized)
        df_bytes = df_serialized.encode('utf-8')

        # Apply compression for large datasets to save session memory
        if len(df_bytes) > compress_threshold:
            buffer = io.BytesIO()
            with gzip.GzipFile(fileobj=buffer, mode='wb', compresslevel=6) as f:
                f.write(df_bytes)

            compressed_data = buffer.getvalue()

            # Only use compression if it actually reduces the size
            if len(compressed_data) < len(df_bytes):
                request.session['df_data'] = list(compressed_data)  # Convert to list for JSON serialization
                request.session['df_compressed'] = True
                logger.info(f"DataFrame compressed: {len(df_bytes)} -> {len(compressed_data)} bytes")
            else:
                # Compression didn't help, store uncompressed
                request.session['df_data'] = df_serialized
                request.session['df_compressed'] = False
        else:
            # Dataset is small enough to store without compression
            request.session['df_data'] = df_serialized
            request.session['df_compressed'] = False

        # Store metadata for quick access without deserializing the entire DataFrame
        # CONSISTENCY FIX: Convert all numpy types to Python native types for JSON serialization
        request.session['df_shape'] = [int(df_optimized.shape[0]), int(df_optimized.shape[1])]  # List of ints, not tuple
        request.session['df_columns'] = list(df_optimized.columns)
        request.session['df_memory_usage'] = int(df_optimized.memory_usage(deep=True).sum())  # Convert to Python int
        request.session.modified = True  # Mark session as modified for Django

        return True

    except Exception as e:
        logger.error(f"Error updating DataFrame in session: {e}")
        return False


@performance_monitor("CSV File Upload Processing")
def process_uploaded_file(uploaded_file, chunk_size=10000):
    """Process and validate uploaded CSV file with memory optimization for large files"""
    if uploaded_file is not None:
        try:
            # Get file size for optimization decisions
            uploaded_file.seek(0, 2)  # Go to end of file
            file_size = uploaded_file.tell()
            uploaded_file.seek(0)  # Go back to beginning
            
            # For files larger than 50MB, use chunked processing
            if file_size > 50 * 1024 * 1024:  # 50MB threshold
                return process_large_csv_file(uploaded_file, chunk_size)
            else:
                # Standard processing for smaller files
                df = pd.read_csv(uploaded_file, low_memory=False)
                return optimize_dataframe_memory(df)
                
        except Exception as e:
            raise ValueError(f"Error reading CSV file: {str(e)}")
    return None


@performance_monitor("Large CSV File Processing")
def process_large_csv_file(uploaded_file, chunk_size=10000):
    """Process large CSV files in chunks to optimize memory usage"""
    try:
        # Read file in chunks
        chunk_list = []
        total_rows = 0
        
        for chunk in pd.read_csv(uploaded_file, chunksize=chunk_size, low_memory=False):
            # Optimize memory for each chunk
            chunk = optimize_dataframe_memory(chunk)
            chunk_list.append(chunk)
            total_rows += len(chunk)

            # Prevent excessive memory usage (limit to ~500K rows for web app)
            if total_rows > 500000:
                logger.warning(f"File truncated to {total_rows} rows for performance")
                break
        
        # Concatenate all chunks
        if chunk_list:
            df = pd.concat(chunk_list, ignore_index=True)
            return df
        else:
            raise ValueError("No data found in CSV file")
            
    except Exception as e:
        raise ValueError(f"Error processing large CSV file: {str(e)}")


@performance_monitor("DataFrame Memory Optimization")
def optimize_dataframe_memory(df):
    """Optimize DataFrame memory usage by converting data types"""
    try:
        # Make a copy to avoid modifying original
        df_optimized = df.copy()
        
        for col in df_optimized.columns:
            col_type = df_optimized[col].dtype
            
            # Optimize numeric columns
            if col_type != 'object':
                c_min = df_optimized[col].min()
                c_max = df_optimized[col].max()
                
                # Integer optimization
                if str(col_type)[:3] == 'int':
                    if c_min > np.iinfo(np.int8).min and c_max < np.iinfo(np.int8).max:
                        df_optimized[col] = df_optimized[col].astype(np.int8)
                    elif c_min > np.iinfo(np.int16).min and c_max < np.iinfo(np.int16).max:
                        df_optimized[col] = df_optimized[col].astype(np.int16)
                    elif c_min > np.iinfo(np.int32).min and c_max < np.iinfo(np.int32).max:
                        df_optimized[col] = df_optimized[col].astype(np.int32)
                
                # Float optimization
                elif str(col_type)[:5] == 'float':
                    if c_min > np.finfo(np.float16).min and c_max < np.finfo(np.float16).max:
                        df_optimized[col] = df_optimized[col].astype(np.float32)
            
            # Optimize string columns with categories
            else:
                num_unique_values = len(df_optimized[col].unique())
                num_total_values = len(df_optimized[col])
                
                # If less than 50% unique values, convert to category
                if num_unique_values / num_total_values < 0.5:
                    df_optimized[col] = df_optimized[col].astype('category')
        
        return df_optimized

    except Exception as e:
        logger.warning(f"Could not optimize DataFrame memory: {e}")
        return df


def check_missing_values(df: pd.DataFrame) -> Dict[str, Any]:
    """Check for missing values in DataFrame

    Args:
        df (pd.DataFrame): DataFrame to analyze

    Returns:
        Dict[str, Any]: Dictionary containing missing value information
    """
    missing_data = df.isnull().sum()
    missing_percentage = (missing_data / len(df) * 100)

    # Create a list of dictionaries for template rendering
    columns_with_missing = []
    for column in missing_data[missing_data > 0].index:
        columns_with_missing.append({
            'column': column,
            'count': int(missing_data[column]),
            'percentage': float(missing_percentage[column])
        })

    missing_info = {
        'missing_counts': missing_data.to_dict(),
        'total_missing': int(missing_data.sum()),
        'columns_with_missing': columns_with_missing,
        'missing_percentage': missing_percentage.to_dict()
    }
    return missing_info


def find_duplicates(df: pd.DataFrame, sample_size: int = 1000) -> Dict[str, Any]:
    """Find duplicate rows in DataFrame with performance optimization for large datasets

    Args:
        df (pd.DataFrame): DataFrame to analyze
        sample_size (int): Maximum number of duplicate rows to return

    Returns:
        Dict[str, Any]: Dictionary containing duplicate information
    """
    duplicated_rows = df.duplicated()
    has_duplicates = duplicated_rows.any()
    duplicate_count = duplicated_rows.sum()
    
    # For large datasets, limit the number of duplicate rows returned
    duplicate_rows = []
    if has_duplicates:
        duplicate_df = df[duplicated_rows]
        if len(duplicate_df) > sample_size:
            # Sample duplicate rows for performance
            duplicate_rows = duplicate_df.sample(n=sample_size).to_dict('records')
        else:
            duplicate_rows = duplicate_df.to_dict('records')
    
    duplicate_info = {
        'has_duplicates': has_duplicates,
        'duplicate_count': int(duplicate_count),
        'duplicate_rows': duplicate_rows,
        'total_rows': len(df),
        'unique_rows': len(df) - int(duplicate_count),
        'sample_size': min(sample_size, int(duplicate_count)) if has_duplicates else 0
    }
    return duplicate_info


def detect_outliers(df, column_name, sample_size=1000):
    """Detect outliers in a specific column using IQR method with performance optimization"""
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")
    
    if not pd.api.types.is_numeric_dtype(df[column_name]):
        raise ValueError(f"Column '{column_name}' is not numeric")
    
    # Calculate IQR using optimized quantile calculation
    column_data = df[column_name].dropna()
    q1 = column_data.quantile(0.25)
    q3 = column_data.quantile(0.75)
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    
    # Find outliers efficiently using boolean indexing
    lower_outlier_mask = df[column_name] < lower_bound
    upper_outlier_mask = df[column_name] > upper_bound
    all_outlier_mask = lower_outlier_mask | upper_outlier_mask
    
    lower_outliers_count = lower_outlier_mask.sum()
    upper_outliers_count = upper_outlier_mask.sum()
    total_outliers = all_outlier_mask.sum()
    
    # For large datasets, sample outliers for performance
    def get_outlier_sample(mask, max_size=sample_size):
        if not mask.any():
            return []
        outlier_df = df[mask]
        if len(outlier_df) > max_size:
            return outlier_df.sample(n=max_size).to_dict('records')
        return outlier_df.to_dict('records')
    
    outlier_info = {
        'column': column_name,
        'lower_bound': float(lower_bound),
        'upper_bound': float(upper_bound),
        'q1': float(q1),
        'q3': float(q3),
        'iqr': float(iqr),
        'lower_outliers_count': int(lower_outliers_count),
        'upper_outliers_count': int(upper_outliers_count),
        'total_outliers': int(total_outliers),
        'outlier_percentage': float((total_outliers / len(df)) * 100),
        'lower_outliers': get_outlier_sample(lower_outlier_mask),
        'upper_outliers': get_outlier_sample(upper_outlier_mask),
        'all_outliers': get_outlier_sample(all_outlier_mask),
        'sample_size': min(sample_size, int(total_outliers)) if total_outliers > 0 else 0
    }
    return outlier_info


def check_data_types(df):
    """Check data types of DataFrame columns"""
    dtypes_info = {
        'column_types': df.dtypes.astype(str).to_dict(),
        'numeric_columns': list(df.select_dtypes(include=[np.number]).columns),
        'categorical_columns': list(df.select_dtypes(include=['object', 'category', 'string']).columns),
        'datetime_columns': list(df.select_dtypes(include=['datetime']).columns),
        'boolean_columns': list(df.select_dtypes(include=['bool']).columns),
        'total_columns': len(df.columns)
    }
    return dtypes_info


def get_basic_info(df):
    """Get basic information about the DataFrame"""
    info = {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': df.dtypes.astype(str).to_dict(),
        'memory_usage': df.memory_usage(deep=True).sum(),
        'null_counts': df.isnull().sum().to_dict(),
        'total_nulls': df.isnull().sum().sum()
    }
    return info


def get_column_statistics(df, column_name, max_categories=100):
    """Get statistical summary for a specific column with performance optimization"""
    if column_name not in df.columns:
        raise ValueError(f"Column '{column_name}' not found in DataFrame")
    
    column = df[column_name].dropna()  # Remove NaN values for calculations
    null_count = df[column_name].isnull().sum()
    
    if pd.api.types.is_numeric_dtype(column):
        # Use efficient quantile calculation for large datasets
        if len(column) > 100000:
            # Sample for very large datasets to speed up calculations
            sample_column = column.sample(n=50000, random_state=42)
            quantiles = sample_column.quantile([0.25, 0.5, 0.75])
            stats = {
                'type': 'numeric',
                'count': int(column.count()),
                'mean': float(column.mean()),
                'median': float(quantiles[0.5]),
                'std': float(column.std()),
                'min': float(column.min()),
                'max': float(column.max()),
                'q25': float(quantiles[0.25]),
                'q75': float(quantiles[0.75]),
                'unique_values': int(column.nunique()),
                'null_count': int(null_count),
                'is_sampled': True,
                'sample_size': 50000
            }
        else:
            stats = {
                'type': 'numeric',
                'count': int(column.count()),
                'mean': float(column.mean()),
                'median': float(column.median()),
                'std': float(column.std()),
                'min': float(column.min()),
                'max': float(column.max()),
                'q25': float(column.quantile(0.25)),
                'q75': float(column.quantile(0.75)),
                'unique_values': int(column.nunique()),
                'null_count': int(null_count),
                'is_sampled': False
            }
    else:
        # For categorical data, limit frequency counts for performance
        value_counts = column.value_counts()
        
        # Limit the number of categories shown
        if len(value_counts) > max_categories:
            top_categories = value_counts.head(max_categories)
            frequency_counts = top_categories.to_dict()
            frequency_counts['... (others)'] = value_counts.iloc[max_categories:].sum()
        else:
            frequency_counts = value_counts.to_dict()
        
        stats = {
            'type': 'categorical',
            'count': int(column.count()),
            'unique_values': int(column.nunique()),
            'most_frequent': column.mode().iloc[0] if not column.mode().empty else None,
            'frequency_counts': frequency_counts,
            'null_count': int(null_count),
            'categories_shown': min(max_categories, len(value_counts)),
            'total_categories': len(value_counts)
        }
    
    return stats


def filter_dataframe(df, filters):
    """Apply filters to DataFrame with automatic type conversion"""
    filtered_df = df.copy()

    for filter_item in filters:
        column = filter_item.get('column')
        value = filter_item.get('value')
        operator = filter_item.get('operator', 'equals')

        if column in filtered_df.columns and value is not None:
            # CONSISTENCY FIX: Auto-convert value type to match column type
            # This handles cases where JSON sends strings but DataFrame has numeric types
            try:
                if pd.api.types.is_numeric_dtype(filtered_df[column]):
                    # Convert value to numeric for numeric columns
                    value = pd.to_numeric(value)
            except (ValueError, TypeError):
                # Keep original value if conversion fails
                pass

            if operator == 'equals':
                filtered_df = filtered_df[filtered_df[column] == value]
            elif operator == 'not_equals':
                filtered_df = filtered_df[filtered_df[column] != value]
            elif operator == 'contains':
                filtered_df = filtered_df[filtered_df[column].astype(str).str.contains(str(value))]
            elif operator == 'greater_than':
                filtered_df = filtered_df[filtered_df[column] > value]
            elif operator == 'less_than':
                filtered_df = filtered_df[filtered_df[column] < value]

    return filtered_df


def select_columns(df, selected_columns):
    """Select specific columns from DataFrame"""
    if not selected_columns:
        return df
    
    # Validate columns exist
    missing_columns = [col for col in selected_columns if col not in df.columns]
    if missing_columns:
        raise ValueError(f"Columns not found: {missing_columns}")
    
    return df[selected_columns]


def replace_values(df, column, old_value, new_value):
    """Replace values in a specific column with improved type handling"""
    if column not in df.columns:
        raise ValueError(f"Column '{column}' not found in DataFrame")
    
    df_copy = df.copy()

    # Basic logging for debugging
    logger.debug(f"Replace Values - Column: {column}, Old: '{old_value}' ({type(old_value).__name__}), New: '{new_value}' ({type(new_value).__name__})")
    logger.debug(f"Replace Values - Column dtype: {df_copy[column].dtype}, Initial matches: {(df_copy[column] == old_value).sum()}")
    
    # Try multiple replacement strategies to handle type mismatches
    replacement_made = False
    
    # Strategy 1: Try exact replacement first
    original_matches = (df_copy[column] == old_value).sum()
    if original_matches > 0:
        logger.debug(f"Replace Values - Using exact match strategy")
        df_copy[column] = df_copy[column].replace(old_value, new_value)
        replacement_made = True

    # Strategy 2: Handle numeric type conversions
    elif pd.api.types.is_numeric_dtype(df_copy[column]):
        logger.debug(f"Replace Values - Using numeric column strategy")
        try:
            old_numeric = pd.to_numeric(old_value)
            new_numeric = pd.to_numeric(new_value)
            
            # Try exact numeric match
            numeric_matches = (df_copy[column] == old_numeric).sum()
            if numeric_matches > 0:
                df_copy[column] = df_copy[column].replace(old_numeric, new_numeric)
                replacement_made = True
            else:
                # Try approximate numeric match for floating point issues
                numeric_mask = abs(df_copy[column] - old_numeric) < 1e-10
                if numeric_mask.any():
                    df_copy.loc[numeric_mask, column] = new_numeric
                    replacement_made = True
        except (ValueError, TypeError):
            pass  # Fall through to string-based strategies
    
    # Strategy 3: String-based comparisons (most common case)
    if not replacement_made:
        logger.debug(f"Replace Values - Using string-based strategy")
        
        # Try string representation matching
        string_mask = df_copy[column].astype(str) == str(old_value)
        if string_mask.any():
            # Convert new_value to appropriate type based on column
            if pd.api.types.is_numeric_dtype(df_copy[column]):
                try:
                    new_value_converted = pd.to_numeric(new_value)
                except (ValueError, TypeError):
                    new_value_converted = new_value
            else:
                new_value_converted = new_value
                
            df_copy.loc[string_mask, column] = new_value_converted
            replacement_made = True
        
        # Try stripped string matching
        elif (df_copy[column].astype(str).str.strip() == str(old_value).strip()).any():
            stripped_mask = df_copy[column].astype(str).str.strip() == str(old_value).strip()
            if pd.api.types.is_numeric_dtype(df_copy[column]):
                try:
                    new_value_converted = pd.to_numeric(new_value)
                except (ValueError, TypeError):
                    new_value_converted = new_value
            else:
                new_value_converted = new_value
                
            df_copy.loc[stripped_mask, column] = new_value_converted
            replacement_made = True
    
    # Strategy 4: Handle special cases (NaN, null, etc.)
    if not replacement_made and str(old_value).lower() in ['nan', 'null', 'none', '']:
        logger.debug(f"Replace Values - Using NaN/null replacement strategy")
        nan_mask = df_copy[column].isna()
        if nan_mask.any():
            df_copy.loc[nan_mask, column] = new_value
            replacement_made = True

    # Log final result
    if replacement_made:
        final_count = (df_copy[column] == new_value).sum()
        logger.debug(f"Replace Values - SUCCESS: {final_count} values replaced")
    else:
        logger.warning(f"Replace Values - No replacements made (possible data type/encoding mismatch)")
    
    return df_copy


def get_dataframe_info(df):
    """Get comprehensive DataFrame information for API responses"""
    return {
        'shape': df.shape,
        'columns': list(df.columns),
        'dtypes': {str(k): str(v) for k, v in df.dtypes.to_dict().items()},
        'memory_usage': f"{df.memory_usage(deep=True).sum() / (1024*1024):.2f} MB",
        'null_counts': df.isnull().sum().to_dict(),
        'total_nulls': int(df.isnull().sum().sum()),
        'total_rows': len(df)
    }


def generate_chart(df, chart_type, x_column=None, y_column=None, color_column=None):
    """Generate chart data for API responses"""
    import plotly.graph_objects as go
    import plotly.express as px
    import plotly.offline as pyo
    
    try:
        fig = None
        
        if chart_type == 'bar' and x_column and y_column:
            if color_column:
                fig = px.bar(df, x=x_column, y=y_column, color=color_column)
            else:
                fig = px.bar(df, x=x_column, y=y_column)
                
        elif chart_type == 'line' and x_column and y_column:
            if color_column:
                fig = px.line(df, x=x_column, y=y_column, color=color_column)
            else:
                fig = px.line(df, x=x_column, y=y_column)
                
        elif chart_type == 'scatter' and x_column and y_column:
            if color_column:
                fig = px.scatter(df, x=x_column, y=y_column, color=color_column)
            else:
                fig = px.scatter(df, x=x_column, y=y_column)
                
        elif chart_type == 'histogram' and x_column:
            fig = px.histogram(df, x=x_column)
            
        elif chart_type == 'pie' and x_column:
            value_counts = df[x_column].value_counts()
            fig = px.pie(values=value_counts.values, names=value_counts.index)
            
        elif chart_type == 'box' and y_column:
            if x_column:
                fig = px.box(df, x=x_column, y=y_column)
            else:
                fig = px.box(df, y=y_column)
                
        elif chart_type == 'heatmap':
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) > 1:
                corr_matrix = df[numeric_cols].corr()
                fig = px.imshow(corr_matrix, text_auto=True)
                
        elif chart_type == 'area' and x_column and y_column:
            fig = px.area(df, x=x_column, y=y_column)
        
        if fig:
            fig.update_layout(
                template='plotly_dark',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            chart_html = pyo.plot(fig, output_type='div', include_plotlyjs=True)
            return {
                'chart_html': chart_html,
                'chart_config': {
                    'chart_type': chart_type,
                    'x_column': x_column,
                    'y_column': y_column,
                    'color_column': color_column
                }
            }
        else:
            raise ValueError("Could not generate chart with provided parameters")
            
    except Exception as e:
        raise ValueError(f"Error generating chart: {str(e)}")


def perform_analysis(df, analysis_type):
    """Perform data analysis and return results"""
    try:
        if analysis_type == 'show_data':
            return {
                'data': df.head(100).to_dict('records'),
                'total_rows': len(df),
                'showing_rows': min(100, len(df))
            }
            
        elif analysis_type == 'missing_values':
            return check_missing_values(df)
            
        elif analysis_type == 'duplicates':
            return find_duplicates(df)
            
        elif analysis_type == 'data_types':
            return check_data_types(df)
            
        elif analysis_type == 'column_stats':
            stats = {}
            for col in df.columns:
                try:
                    stats[col] = get_column_statistics(df, col)
                except Exception as e:
                    stats[col] = {'error': str(e)}
            return stats
            
        elif analysis_type == 'outliers':
            numeric_cols = df.select_dtypes(include=['number']).columns
            if len(numeric_cols) == 0:
                return {'error': 'No numeric columns found for outlier detection'}
            
            outliers_info = {}
            for col in numeric_cols[:5]:  # Limit to first 5 numeric columns
                try:
                    outliers_info[col] = detect_outliers(df, col)
                except Exception as e:
                    outliers_info[col] = {'error': str(e)}
            return outliers_info
            
        else:
            raise ValueError(f"Unknown analysis type: {analysis_type}")
            
    except Exception as e:
        raise ValueError(f"Error performing analysis: {str(e)}")


def apply_preprocessing_operation(df, operation_data):
    """Apply preprocessing operation to DataFrame"""
    try:
        operation = operation_data.get('operation')
        df_copy = df.copy()
        
        if operation == 'select_columns':
            columns = operation_data.get('columns', [])
            if not columns:
                return {'success': False, 'message': 'No columns specified'}
            df_copy = select_columns(df_copy, columns)
            return {
                'success': True,
                'message': f'Selected {len(columns)} columns',
                'dataframe': df_copy
            }
            
        elif operation == 'drop_columns':
            columns = operation_data.get('columns', [])
            if not columns:
                return {'success': False, 'message': 'No columns specified'}
            df_copy = df_copy.drop(columns=columns, errors='ignore')
            return {
                'success': True,
                'message': f'Dropped {len(columns)} columns',
                'dataframe': df_copy
            }
            
        elif operation == 'replace_values':
            column = operation_data.get('column')
            old_value = operation_data.get('old_value')
            new_value = operation_data.get('new_value')
            
            if not column or old_value is None or new_value is None:
                return {'success': False, 'message': 'Missing required parameters'}
                
            df_copy = replace_values(df_copy, column, old_value, new_value)
            return {
                'success': True,
                'message': f'Replaced values in column {column}',
                'dataframe': df_copy
            }
            
        elif operation == 'remove_duplicates':
            original_count = len(df_copy)
            df_copy = df_copy.drop_duplicates()
            removed_count = original_count - len(df_copy)
            return {
                'success': True,
                'message': f'Removed {removed_count} duplicate rows',
                'dataframe': df_copy
            }
            
        elif operation == 'handle_missing_values':
            strategy = operation_data.get('missing_strategy', 'drop')
            columns = operation_data.get('columns', [])
            
            if strategy == 'drop':
                if columns:
                    df_copy = df_copy.dropna(subset=columns)
                else:
                    df_copy = df_copy.dropna()
                    
            elif strategy in ['fill_mean', 'fill_median', 'fill_mode']:
                numeric_cols = df_copy.select_dtypes(include=['number']).columns
                target_cols = columns if columns else numeric_cols
                
                for col in target_cols:
                    if col in df_copy.columns:
                        if strategy == 'fill_mean':
                            df_copy[col] = df_copy[col].fillna(df_copy[col].mean())
                        elif strategy == 'fill_median':
                            df_copy[col] = df_copy[col].fillna(df_copy[col].median())
                        elif strategy == 'fill_mode':
                            mode_val = df_copy[col].mode()
                            if not mode_val.empty:
                                df_copy[col] = df_copy[col].fillna(mode_val.iloc[0])
                                
            elif strategy == 'fill_value':
                fill_value = operation_data.get('fill_value')
                if fill_value is not None:
                    if columns:
                        for col in columns:
                            if col in df_copy.columns:
                                df_copy[col] = df_copy[col].fillna(fill_value)
                    else:
                        df_copy = df_copy.fillna(fill_value)
                        
            return {
                'success': True,
                'message': f'Applied missing value strategy: {strategy}',
                'dataframe': df_copy
            }
            
        elif operation == 'filter_data':
            filter_conditions = operation_data.get('filter_conditions', [])
            if filter_conditions:
                df_copy = filter_dataframe(df_copy, filter_conditions)
                
            return {
                'success': True,
                'message': f'Applied {len(filter_conditions)} filters',
                'dataframe': df_copy
            }
            
        elif operation == 'reset_data':
            return {
                'success': True,
                'message': 'Data will be reset to original state',
                'dataframe': df  # Return original dataframe
            }
            
        else:
            return {'success': False, 'message': f'Unknown operation: {operation}'}
            
    except Exception as e:
        return {'success': False, 'message': f'Error applying operation: {str(e)}'}


def export_dataframe(df: pd.DataFrame, format: str) -> Tuple[bytes, str, str]:
    """Export DataFrame in specified format

    Args:
        df (pd.DataFrame): DataFrame to export
        format (str): Export format ('csv', 'json', or 'excel')

    Returns:
        Tuple[bytes, str, str]: Content bytes, MIME type, and file extension

    Raises:
        ValueError: If format is unsupported or export fails
    """
    try:
        if format == 'csv':
            output = io.StringIO()
            df.to_csv(output, index=False)
            content = output.getvalue().encode('utf-8')
            return content, 'text/csv', 'csv'

        elif format == 'json':
            content = df.to_json(orient='records', indent=2).encode('utf-8')
            return content, 'application/json', 'json'

        elif format == 'excel':
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df.to_excel(writer, sheet_name='Data', index=False)
            content = output.getvalue()
            return content, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet', 'xlsx'

        else:
            raise ValueError(f"Unsupported export format: {format}")

    except Exception as e:
        raise ValueError(f"Error exporting data: {str(e)}")