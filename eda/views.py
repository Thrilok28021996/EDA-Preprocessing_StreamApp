# Django imports for web framework functionality
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from django.template.loader import render_to_string

# Standard library imports
import json
import logging

# Configure logging
logger = logging.getLogger(__name__)

# Data science libraries for analysis and visualization
import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import plotly

# Custom utility functions for data processing
from utils import (
    get_dataframe_from_session,  # Retrieve DataFrame from Django session
    check_missing_values,        # Analyze missing data patterns
    find_duplicates,             # Identify duplicate rows
    detect_outliers,             # Statistical outlier detection
    check_data_types,            # Analyze column data types
    get_basic_info,              # Get basic DataFrame information
    get_column_statistics        # Calculate column-specific statistics
)

# Import advanced chart generation functions with graceful fallback
try:
    from .new_charts import (
        generate_violin_chart,      # Violin plots for distribution visualization
        generate_donut_chart,       # Donut charts (pie charts with center hole)
        generate_bubble_chart,      # Bubble charts for 3D data visualization
        generate_treemap_chart,     # Hierarchical data visualization
        generate_sunburst_chart,    # Multi-level pie charts
        generate_radar_chart        # Radar/spider charts for multivariate data
    )
except ImportError as e:
    import logging
    logging.getLogger(__name__).warning(f"Could not import new chart functions: {e}")
    
    # Define placeholder functions to prevent application crashes
    # These functions raise informative errors when advanced charts are unavailable
    def generate_violin_chart(df, options):
        raise ValueError("Violin chart not available")
    def generate_donut_chart(df, options):
        raise ValueError("Donut chart not available")
    def generate_bubble_chart(df, options):
        raise ValueError("Bubble chart not available")
    def generate_treemap_chart(df, options):
        raise ValueError("Treemap chart not available")
    def generate_sunburst_chart(df, options):
        raise ValueError("Sunburst chart not available")
    def generate_radar_chart(df, options):
        raise ValueError("Radar chart not available")


def index(request):
    """EDA main page with analysis options
    
    This view handles the main Exploratory Data Analysis page where users can:
    - View basic dataset information
    - Select columns for analysis
    - Generate various types of charts
    - Perform statistical analysis
    
    Returns:
        Rendered EDA index template with dataset information and column lists
    """
    # Check if user has uploaded a dataset
    if not request.session.get('df_uploaded', False):
        messages.warning(request, 'Please upload a CSV file in the Home page to get started.')
        return render(request, 'eda/index.html', {'no_data': True})
    
    # Retrieve DataFrame from Django session storage
    df = get_dataframe_from_session(request)
    if df is None:
        messages.error(request, 'Error loading dataset from session. Please re-upload your CSV file.')
        return render(request, 'eda/index.html', {'no_data': True})
    
    # Extract basic dataset metadata for display
    basic_info = get_basic_info(df)
    
    # Classify columns by data type for appropriate chart/analysis selection
    numeric_columns = df.select_dtypes(include=[np.number]).columns.tolist()
    categorical_columns = df.select_dtypes(include=['object', 'category', 'string']).columns.tolist()
    
    # Enhanced categorical detection: identify columns that behave categorically
    # even if they're stored as other data types (e.g., numeric codes)
    for col in df.columns:
        if col not in numeric_columns and col not in categorical_columns:
            # Apply heuristic: if less than 50% unique values and fewer than 50 categories,
            # treat as categorical for better visualization options
            if df[col].nunique() / len(df) < 0.5 and df[col].nunique() < 50:
                categorical_columns.append(col)
    
    # Prepare template context with all necessary data
    context = {
        'df_info': basic_info,                    # Basic dataset statistics
        'numeric_columns': numeric_columns,       # Columns suitable for numerical analysis
        'categorical_columns': categorical_columns, # Columns suitable for categorical analysis
        'all_columns': df.columns.tolist()       # Complete list of all columns
    }
    
    return render(request, 'eda/index.html', context)


@require_http_methods(["POST"])
def generate_chart(request):
    """Generate interactive charts using Plotly
    
    This view handles AJAX requests to generate various types of interactive charts.
    Supports multiple chart types including: bar, line, histogram, pie, scatter, box,
    heatmap, area, violin, donut, bubble, treemap, sunburst, and radar charts.
    
    Request format (JSON):
        {
            'chart_type': 'bar',  # Type of chart to generate
            'options': {          # Chart-specific options
                'x_column': 'column_name',
                'y_column': 'column_name',
                'bins': 20,       # For histograms
                'aggregation': 'mean'  # For grouped charts
            }
        }
    
    Returns:
        JSON response with chart data in Plotly format or error message
    """
    # Only accept POST requests for security and proper data handling
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests allowed'})
    
    # Retrieve the current dataset from session
    df = get_dataframe_from_session(request)
    if df is None:
        return JsonResponse({'success': False, 'error': 'No dataset found in session'})
    
    try:
        # Parse the JSON request body
        data = json.loads(request.body)
        chart_type = data.get('chart_type')
        options = data.get('options', {})
        
        # Debug logging for troubleshooting chart generation issues
        logger.debug(f"Chart Type: {chart_type}, Options: {options}")
        logger.debug(f"DataFrame shape: {df.shape}, columns: {list(df.columns)}")
        
        # Route to appropriate chart generation function based on chart type
        if chart_type == 'bar':
            logger.debug("Generating bar chart")
            chart_data = generate_bar_chart(df, options)  # Bar charts for categorical data
            logger.debug("Bar chart generated successfully")
        elif chart_type == 'line':
            chart_data = generate_line_chart(df, options)  # Line charts for trends over time
        elif chart_type == 'histogram':
            chart_data = generate_histogram(df, options)   # Distribution visualization
        elif chart_type == 'pie':
            chart_data = generate_pie_chart(df, options)   # Proportional data visualization
        elif chart_type == 'scatter':
            chart_data = generate_scatter_chart(df, options)  # Correlation visualization
        elif chart_type == 'box':
            chart_data = generate_box_chart(df, options)   # Statistical distribution summary
        elif chart_type == 'heatmap':
            chart_data = generate_heatmap(df, options)     # Correlation matrix visualization
        elif chart_type == 'area':
            chart_data = generate_area_chart(df, options)  # Filled line charts
        elif chart_type == 'violin':
            chart_data = generate_violin_chart(df, options)  # Distribution shape visualization
        elif chart_type == 'donut':
            chart_data = generate_donut_chart(df, options)   # Pie chart variant
        elif chart_type == 'bubble':
            chart_data = generate_bubble_chart(df, options)  # 3-dimensional scatter plots
        elif chart_type == 'treemap':
            chart_data = generate_treemap_chart(df, options) # Hierarchical data visualization
        elif chart_type == 'sunburst':
            chart_data = generate_sunburst_chart(df, options) # Multi-level pie charts
        elif chart_type == 'radar':
            chart_data = generate_radar_chart(df, options)   # Multi-variable comparison
        else:
            return JsonResponse({'success': False, 'error': f'Unknown chart type: {chart_type}'})
        
        # Convert Plotly figure object to JSON format for frontend consumption
        try:
            # Serialize the Plotly figure to JSON format that can be sent to the browser
            chart_json = json.loads(plotly.io.to_json(chart_data['fig']))
            logger.debug("Successfully converted chart to JSON")

            # Return chart data and layout separately for frontend Plotly.js rendering
            return JsonResponse({
                'success': True,
                'chart_data': chart_json['data'],    # Chart data points and series
                'layout': chart_json['layout']       # Chart styling and configuration
            })
        except Exception as json_error:
            logger.error(f"Chart serialization error: {json_error}")
            return JsonResponse({'success': False, 'error': f'Chart serialization error: {str(json_error)}'})

    except Exception as e:
        logger.error(f"Chart generation error: {e}")
        return JsonResponse({'success': False, 'error': str(e)})


@require_http_methods(["POST"])
def analyze_data(request):
    """Perform data analysis operations
    
    This view handles various data analysis requests including:
    - Missing value analysis
    - Duplicate detection
    - Outlier identification
    - Data type analysis
    - Column-specific statistics
    - Data preview/display
    
    Request format (JSON):
        {
            'analysis_type': 'missing_values',  # Type of analysis to perform
            'options': {
                'column': 'column_name'  # For column-specific analysis
            }
        }
    
    Returns:
        JSON response with analysis results rendered as HTML
    """
    # Only accept POST requests for consistency and security
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Only POST requests allowed'})
    
    # Retrieve the dataset from session storage
    df = get_dataframe_from_session(request)
    if df is None:
        return JsonResponse({'success': False, 'error': 'No dataset found in session'})
    
    try:
        # Parse the analysis request
        data = json.loads(request.body)
        analysis_type = data.get('analysis_type')
        options = data.get('options', {})
        
        # Route to appropriate analysis function and render results
        if analysis_type == 'missing_values':
            # Analyze patterns of missing data across all columns
            result = check_missing_values(df)
            html = render_to_string('eda/analysis/missing_values.html', {'result': result})
            
        elif analysis_type == 'duplicates':
            # Identify and count duplicate rows in the dataset
            result = find_duplicates(df)
            html = render_to_string('eda/analysis/duplicates.html', {'result': result})
            
        elif analysis_type == 'outliers':
            # Detect statistical outliers in a specific numeric column
            column = options.get('column')
            if not column or column not in df.columns:
                return JsonResponse({'success': False, 'error': 'Valid column name required'})
            result = detect_outliers(df, column)
            html = render_to_string('eda/analysis/outliers.html', {'result': result})
            
        elif analysis_type == 'data_types':
            # Analyze and categorize data types of all columns
            result = check_data_types(df)
            html = render_to_string('eda/analysis/data_types.html', {'result': result})
            
        elif analysis_type == 'column_stats':
            # Generate comprehensive statistics for a specific column
            column = options.get('column')
            if not column or column not in df.columns:
                return JsonResponse({'success': False, 'error': 'Valid column name required'})
            result = get_column_statistics(df, column)
            html = render_to_string('eda/analysis/column_stats.html', {'result': result, 'column': column})
            
        elif analysis_type == 'show_data':
            # Display a sample of the raw data in table format
            df_sample = df.head(100)  # Limit to first 100 rows for performance
            html = render_to_string('eda/analysis/show_data.html', {
                'df_sample': df_sample,
                'columns': df_sample.columns.tolist(),
                'data': df_sample.values.tolist(),
                'total_rows': len(df),
                'showing_rows': len(df_sample)
            })
        else:
            return JsonResponse({'success': False, 'error': f'Unknown analysis type: {analysis_type}'})
        
        return JsonResponse({'success': True, 'html': html})
        
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)})


# ============================================================================
# CHART GENERATION FUNCTIONS
# ============================================================================
# These functions create interactive Plotly charts from pandas DataFrames.
# Each function handles specific chart types with customizable options.

def generate_bar_chart(df, options):
    """Generate bar chart using Plotly with support for both frequency and custom modes
    
    Supports two modes:
    1. Frequency mode: Counts occurrences of values in x_column
    2. Custom mode: Aggregates y_column values grouped by x_column
    
    Args:
        df (DataFrame): Source data
        options (dict): Chart configuration including:
            - x_column: Column for x-axis categories
            - y_column: Column for y-axis values (custom mode)
            - chart_mode: 'frequency' or 'custom'
            - aggregation: 'mean', 'sum', or 'median' for custom mode
    
    Returns:
        dict: Contains Plotly figure object
    """
    # Extract and validate required parameters
    x_column = options.get('x_column')
    if not x_column or x_column not in df.columns:
        raise ValueError('Valid x_column required for bar chart')
    
    # Extract optional parameters with defaults
    y_column = options.get('y_column')
    chart_mode = options.get('chart_mode', 'frequency')  # Default to frequency counting
    aggregation = options.get('aggregation', 'mean')     # Default aggregation method
    
    if chart_mode == 'custom' and y_column and y_column in df.columns:
        # Custom mode: use x_column as categories and aggregate y_column values
        if pd.api.types.is_numeric_dtype(df[y_column]):
            if aggregation == 'mean':
                grouped_data = df.groupby(x_column)[y_column].mean()
                y_title = f'Average {y_column}'
            elif aggregation == 'sum':
                grouped_data = df.groupby(x_column)[y_column].sum()
                y_title = f'Sum of {y_column}'
            elif aggregation == 'median':
                grouped_data = df.groupby(x_column)[y_column].median()
                y_title = f'Median {y_column}'
            else:
                grouped_data = df.groupby(x_column)[y_column].mean()
                y_title = f'Average {y_column}'
            
            x_data = grouped_data.index.astype(str)
            y_data = grouped_data.values
            chart_title = f'{y_title} by {x_column}'
            bar_name = f'{y_title}'
        else:
            # If y_column is not numeric, fall back to frequency counting
            value_counts = df[x_column].value_counts()
            x_data = value_counts.index.astype(str)
            y_data = value_counts.values
            chart_title = f'Value Counts for {x_column}'
            y_title = 'Count'
            bar_name = f'Count of {x_column}'
    else:
        # Frequency mode: count occurrences of x_column values
        value_counts = df[x_column].value_counts()
        x_data = value_counts.index.astype(str)
        y_data = value_counts.values
        chart_title = f'Value Counts for {x_column}'
        y_title = 'Count'
        bar_name = f'Count of {x_column}'
    
    fig = go.Figure(data=[
        go.Bar(
            x=x_data,
            y=y_data,
            marker_color='#0083B8',
            name=bar_name
        )
    ])
    
    fig.update_layout(
        title=chart_title,
        xaxis_title=x_column,
        yaxis_title=y_title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_line_chart(df, options):
    """Generate line chart using Plotly with support for both frequency and custom modes"""
    x_column = options.get('x_column')
    if not x_column or x_column not in df.columns:
        raise ValueError('Valid x_column required for line chart')
    
    y_column = options.get('y_column')
    chart_mode = options.get('chart_mode', 'frequency')
    aggregation = options.get('aggregation', 'mean')
    
    if chart_mode == 'custom' and y_column and y_column in df.columns:
        # Custom mode: use x_column and y_column for actual line relationships
        if pd.api.types.is_numeric_dtype(df[y_column]):
            if aggregation == 'mean':
                grouped_data = df.groupby(x_column)[y_column].mean().sort_index()
                y_title = f'Average {y_column}'
            elif aggregation == 'sum':
                grouped_data = df.groupby(x_column)[y_column].sum().sort_index()
                y_title = f'Sum of {y_column}'
            elif aggregation == 'median':
                grouped_data = df.groupby(x_column)[y_column].median().sort_index()
                y_title = f'Median {y_column}'
            else:
                grouped_data = df.groupby(x_column)[y_column].mean().sort_index()
                y_title = f'Average {y_column}'
            
            # Handle different x-axis data types for proper sorting
            if pd.api.types.is_numeric_dtype(df[x_column]):
                x_data = grouped_data.index
                x_data_str = x_data.astype(str)
            elif pd.api.types.is_datetime64_any_dtype(df[x_column]):
                x_data = grouped_data.index
                x_data_str = x_data.astype(str)
            else:
                x_data = grouped_data.index
                x_data_str = x_data.astype(str)
            
            y_data = grouped_data.values
            chart_title = f'{y_title} by {x_column}'
            line_name = f'{y_title}'
        else:
            # If y_column is not numeric, fall back to frequency counting
            value_counts = df[x_column].value_counts().sort_index()
            x_data_str = value_counts.index.astype(str)
            y_data = value_counts.values
            chart_title = f'Value Counts for {x_column}'
            y_title = 'Count'
            line_name = f'Count of {x_column}'
    else:
        # Frequency mode: count occurrences of x_column values
        value_counts = df[x_column].value_counts().sort_index()
        x_data_str = value_counts.index.astype(str)
        y_data = value_counts.values
        chart_title = f'Line Chart for {x_column}'
        y_title = 'Count'
        line_name = f'Count of {x_column}'
    
    fig = go.Figure(data=[
        go.Scatter(
            x=x_data_str,
            y=y_data,
            mode='lines+markers',
            line=dict(color='#0083B8'),
            name=line_name
        )
    ])
    
    fig.update_layout(
        title=chart_title,
        xaxis_title=x_column,
        yaxis_title=y_title,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_histogram(df, options):
    """Generate histogram using Plotly with custom binning options"""
    column = options.get('column')
    if not column or column not in df.columns:
        raise ValueError('Valid column required for histogram')
    
    bins = options.get('bins', 'auto')
    bin_size = options.get('bin_size')
    
    # Prepare histogram parameters
    hist_params = {
        'x': df[column],
        'marker_color': '#00d084',
        'name': column
    }
    
    # Handle binning options
    if bins == 'custom' and bin_size:
        try:
            hist_params['nbinsx'] = int(bin_size)
        except (ValueError, TypeError):
            # Fall back to auto if custom bin size is invalid
            pass
    elif bins != 'auto':
        try:
            hist_params['nbinsx'] = int(bins)
        except (ValueError, TypeError):
            # Fall back to auto if bins value is invalid
            pass
    
    fig = go.Figure(data=[go.Histogram(**hist_params)])
    
    # Create title based on binning
    if 'nbinsx' in hist_params:
        title = f'Histogram of {column} ({hist_params["nbinsx"]} bins)'
    else:
        title = f'Histogram of {column}'
    
    fig.update_layout(
        title=title,
        xaxis_title=column,
        yaxis_title='Frequency',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_pie_chart(df, options):
    """Generate pie chart using Plotly"""
    column = options.get('column')
    if not column or column not in df.columns:
        raise ValueError('Valid column required for pie chart')
    
    value_counts = df[column].value_counts()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=value_counts.index.astype(str),
            values=value_counts.values,
            name=column
        )
    ])
    
    fig.update_layout(
        title=f'Pie Chart for {column}',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_scatter_chart(df, options):
    """Generate scatter plot using Plotly"""
    x_column = options.get('x_column')
    y_column = options.get('y_column')
    
    if not x_column or x_column not in df.columns:
        raise ValueError('Valid x_column required for scatter plot')
    if not y_column or y_column not in df.columns:
        raise ValueError('Valid y_column required for scatter plot')
    
    fig = go.Figure(data=[
        go.Scatter(
            x=df[x_column],
            y=df[y_column],
            mode='markers',
            marker=dict(color='#0083B8'),
            name=f'{x_column} vs {y_column}'
        )
    ])
    
    fig.update_layout(
        title=f'Scatter Plot: {x_column} vs {y_column}',
        xaxis_title=x_column,
        yaxis_title=y_column,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_box_chart(df, options):
    """Generate box plot using Plotly with optional grouping"""
    column = options.get('column')
    if not column or column not in df.columns:
        raise ValueError('Valid column required for box plot')
    
    group_by = options.get('group_by')
    
    if group_by and group_by in df.columns and group_by != column:
        # Grouped box plot
        fig = go.Figure()
        
        # Get unique groups and sort them for consistent display
        unique_groups = sorted(df[group_by].dropna().unique())
        
        for group_value in unique_groups:
            group_data = df[df[group_by] == group_value][column].dropna()
            if len(group_data) > 0:  # Only add if there's data
                fig.add_trace(go.Box(
                    y=group_data,
                    name=str(group_value),
                    marker_color='#00d084'
                ))
        
        title = f'Box Plot of {column} by {group_by}'
        xaxis_title = group_by
    else:
        # Single box plot
        fig = go.Figure(data=[
            go.Box(
                y=df[column].dropna(),
                name=column,
                marker_color='#00d084'
            )
        ])
        
        title = f'Box Plot of {column}'
        xaxis_title = ''
    
    fig.update_layout(
        title=title,
        xaxis_title=xaxis_title,
        yaxis_title=column,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_heatmap(df, options):
    """Generate correlation heatmap using Plotly"""
    columns = options.get('columns', [])
    if not columns:
        # Use all numeric columns
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
        if len(numeric_cols) < 2:
            raise ValueError('At least 2 numeric columns required for heatmap')
        columns = numeric_cols
    
    # Calculate correlation matrix
    corr_matrix = df[columns].corr()
    
    fig = go.Figure(data=[
        go.Heatmap(
            z=corr_matrix.values,
            x=corr_matrix.columns,
            y=corr_matrix.columns,
            colorscale='RdBu',
            zmid=0,
            text=corr_matrix.values.round(2),
            texttemplate='%{text}',
            textfont={"size": 10}
        )
    ])
    
    fig.update_layout(
        title='Correlation Heatmap',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_area_chart(df, options):
    """Generate area chart using Plotly"""
    x_column = options.get('x_column')
    y_column = options.get('y_column')
    
    if not x_column or x_column not in df.columns:
        raise ValueError('Valid x_column required for area chart')
    if not y_column or y_column not in df.columns:
        raise ValueError('Valid y_column required for area chart')
    
    # Sort by x_column for better visualization
    df_sorted = df.sort_values(x_column)
    
    fig = go.Figure(data=[
        go.Scatter(
            x=df_sorted[x_column],
            y=df_sorted[y_column],
            fill='tonexty',
            mode='lines',
            line=dict(color='#00d084'),
            name=f'{y_column} over {x_column}'
        )
    ])
    
    fig.update_layout(
        title=f'Area Chart: {y_column} over {x_column}',
        xaxis_title=x_column,
        yaxis_title=y_column,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}
