"""
Advanced Chart Generation Module

This module provides specialized chart generation functions using Plotly for
advanced data visualization in the EDA application. Each function creates
interactive charts with custom styling optimized for dark themes.

Supported chart types:
- Violin plots: Distribution visualization with kernel density estimation
- Donut charts: Pie charts with center holes for better readability
- Bubble charts: 3D scatter plots with size-encoded third dimension
- Treemaps: Hierarchical data visualization using nested rectangles
- Sunburst charts: Multi-level pie charts for hierarchical data
- Radar charts: Multi-variable comparison in polar coordinates

All charts are styled with dark theme compatibility and responsive design.
"""

# Plotly imports for interactive chart generation
import plotly.graph_objects as go

# Pandas for data manipulation
import pandas as pd

def generate_violin_chart(df, options):
    """Generate violin plot using Plotly with optional grouping
    
    Violin plots show the distribution shape of numeric data, combining
    aspects of box plots and kernel density estimation. They're excellent
    for comparing distributions across different groups.
    
    Args:
        df (DataFrame): Source data
        options (dict): Chart options including:
            - column: Numeric column for distribution analysis
            - group_by: Optional grouping column for comparison
    
    Returns:
        dict: Contains Plotly figure object ready for rendering
    
    Features:
        - Shows distribution shape and density
        - Includes box plot overlay for quartile information
        - Mean line for central tendency
        - Support for grouped comparisons
    """
    # Validate required parameters
    column = options.get('column')
    if not column or column not in df.columns:
        raise ValueError('Valid column required for violin plot')
    
    # Optional grouping for comparative analysis
    group_by = options.get('group_by')
    
    if group_by and group_by in df.columns and group_by != column:
        # Create grouped violin plot for comparative analysis
        fig = go.Figure()
        
        # Sort groups for consistent display order
        unique_groups = sorted(df[group_by].dropna().unique())
        
        # Generate separate violin for each group
        for group_value in unique_groups:
            group_data = df[df[group_by] == group_value][column].dropna()
            if len(group_data) > 0:  # Skip empty groups
                fig.add_trace(go.Violin(
                    y=group_data,
                    name=str(group_value),
                    box_visible=True,        # Show quartile box overlay
                    meanline_visible=True,   # Show mean line
                    fillcolor='#0083B8',     # Blue fill color
                    opacity=0.7,             # Semi-transparent for better visibility
                    line_color='white'       # White outline for dark theme
                ))
        
        title = f'Violin Plot of {column} by {group_by}'
        xaxis_title = group_by
    else:
        # Create single violin plot for overall distribution
        fig = go.Figure(data=[
            go.Violin(
                y=df[column].dropna(),    # Remove NaN values
                name=column,
                box_visible=True,         # Include box plot overlay
                meanline_visible=True,    # Show mean line
                fillcolor='#0083B8',      # Consistent blue color scheme
                opacity=0.7,
                line_color='white'
            )
        ])
        
        title = f'Violin Plot of {column}'
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


def generate_donut_chart(df, options):
    """Generate donut chart using Plotly
    
    Donut charts are pie charts with a center hole, providing better
    readability and space for additional information display.
    Ideal for showing proportional relationships in categorical data.
    
    Args:
        df (DataFrame): Source data
        options (dict): Chart options including:
            - column: Categorical column for proportion analysis
    
    Returns:
        dict: Contains Plotly figure object
    
    Features:
        - Center hole for improved readability
        - Automatic value counting and percentage calculation
        - Center text annotation with column name
        - Dark theme optimized styling
    """
    # Validate required column parameter
    column = options.get('column')
    if not column or column not in df.columns:
        raise ValueError('Valid column required for donut chart')
    
    # Calculate value frequencies for proportional display
    value_counts = df[column].value_counts()
    
    fig = go.Figure(data=[
        go.Pie(
            labels=value_counts.index.astype(str),
            values=value_counts.values,
            hole=0.4,
            name=column
        )
    ])
    
    fig.update_layout(
        title=f'Donut Chart for {column}',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'},
        annotations=[dict(text=column, x=0.5, y=0.5, font_size=20, showarrow=False)]
    )
    
    return {'fig': fig}


def generate_bubble_chart(df, options):
    """Generate bubble chart using Plotly
    
    Bubble charts extend scatter plots by encoding a third dimension
    through bubble size, enabling visualization of three variables
    simultaneously. Excellent for exploring relationships between
    multiple quantitative variables.
    
    Args:
        df (DataFrame): Source data
        options (dict): Chart options including:
            - x_column: Numeric column for x-axis
            - y_column: Numeric column for y-axis  
            - size_column: Numeric column for bubble size encoding
    
    Returns:
        dict: Contains Plotly figure object
    
    Features:
        - Three-dimensional data visualization
        - Automatic size scaling and normalization
        - Color-coded by size for additional clarity
        - Viridis colorscale for accessibility
    """
    # Validate all required parameters for 3D visualization
    x_column = options.get('x_column')
    y_column = options.get('y_column')  
    size_column = options.get('size_column')
    
    if not x_column or x_column not in df.columns:
        raise ValueError('Valid x_column required for bubble chart')
    if not y_column or y_column not in df.columns:
        raise ValueError('Valid y_column required for bubble chart')
    if not size_column or size_column not in df.columns:
        raise ValueError('Valid size_column required for bubble chart')
    
    fig = go.Figure(data=[
        go.Scatter(
            x=df[x_column],
            y=df[y_column],
            mode='markers',
            marker=dict(
                size=df[size_column],
                sizemode='diameter',
                sizeref=2.*max(df[size_column])/(40.**2),
                sizemin=4,
                color=df[size_column],
                colorscale='Viridis',
                showscale=True
            ),
            name=f'{x_column} vs {y_column}'
        )
    ])
    
    fig.update_layout(
        title=f'Bubble Chart: {x_column} vs {y_column} (size: {size_column})',
        xaxis_title=x_column,
        yaxis_title=y_column,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_treemap_chart(df, options):
    """Generate treemap using Plotly
    
    Treemaps visualize hierarchical data using nested rectangles,
    where the size of each rectangle represents a quantitative value.
    Excellent for showing proportional relationships and hierarchies.
    
    Args:
        df (DataFrame): Source data
        options (dict): Chart options including:
            - category_column: Column defining categories/groups
            - value_column: Optional numeric column for sizing (uses count if not provided)
    
    Returns:
        dict: Contains Plotly figure object
    
    Features:
        - Hierarchical data visualization
        - Automatic size calculation from data
        - Support for both value-based and count-based sizing
        - Informative labels with values and percentages
    """
    # Validate required parameters
    category_column = options.get('category_column')
    value_column = options.get('value_column')
    
    if not category_column or category_column not in df.columns:
        raise ValueError('Valid category_column required for treemap')
    
    if value_column and value_column in df.columns:
        # Use specified value column
        grouped_data = df.groupby(category_column)[value_column].sum().reset_index()
        values = grouped_data[value_column]
    else:
        # Use count of occurrences
        grouped_data = df[category_column].value_counts().reset_index()
        grouped_data.columns = [category_column, 'count']
        values = grouped_data['count']
    
    fig = go.Figure(data=[
        go.Treemap(
            labels=grouped_data[category_column],
            values=values,
            textinfo="label+value+percent parent"
        )
    ])
    
    fig.update_layout(
        title=f'Treemap of {category_column}',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_sunburst_chart(df, options):
    """Generate sunburst chart using Plotly
    
    Sunburst charts are multi-level pie charts that display hierarchical
    data in a radial layout. Each ring represents a level in the hierarchy,
    making it ideal for exploring categorical data structures.
    
    Args:
        df (DataFrame): Source data
        options (dict): Chart options including:
            - category_column: Column defining categories
            - value_column: Optional numeric column for sizing (uses count if not provided)
    
    Returns:
        dict: Contains Plotly figure object
    
    Features:
        - Radial hierarchical visualization
        - Interactive drill-down capabilities
        - Automatic value aggregation
        - Responsive design for different screen sizes
    """
    # Validate required parameters
    category_column = options.get('category_column')
    value_column = options.get('value_column')
    
    if not category_column or category_column not in df.columns:
        raise ValueError('Valid category_column required for sunburst')
    
    if value_column and value_column in df.columns:
        # Use specified value column
        grouped_data = df.groupby(category_column)[value_column].sum().reset_index()
        values = grouped_data[value_column]
    else:
        # Use count of occurrences
        grouped_data = df[category_column].value_counts().reset_index()
        grouped_data.columns = [category_column, 'count']
        values = grouped_data['count']
    
    fig = go.Figure(data=[
        go.Sunburst(
            labels=grouped_data[category_column],
            values=values,
            parents=[""] * len(grouped_data)
        )
    ])
    
    fig.update_layout(
        title=f'Sunburst Chart of {category_column}',
        paper_bgcolor='rgba(0,0,0,0)',
        font={'color': 'white'}
    )
    
    return {'fig': fig}


def generate_radar_chart(df, options):
    """Generate radar chart using Plotly
    
    Radar charts (also known as spider charts) display multivariate data
    in a circular format, with each variable represented on a separate axis.
    Ideal for comparing multiple quantitative variables simultaneously.
    
    Args:
        df (DataFrame): Source data
        options (dict): Chart options including:
            - columns: List of numeric columns to include in the radar
    
    Returns:
        dict: Contains Plotly figure object
    
    Features:
        - Multi-variable comparison in polar coordinates
        - Automatic data normalization (0-100 scale)
        - Mean value calculation for each variable
        - Closed polygon for easy pattern recognition
        - Robust handling of data with no variation
    """
    # Validate that at least one column is specified
    columns = options.get('columns', [])
    if not columns:
        raise ValueError('At least one column required for radar chart')
    
    # Filter to only valid numeric columns for mathematical operations
    valid_columns = [col for col in columns if col in df.columns and pd.api.types.is_numeric_dtype(df[col])]
    if not valid_columns:
        raise ValueError('Valid numeric columns required for radar chart')
    
    # Calculate mean values for each column as the representative value
    mean_values = df[valid_columns].mean()
    
    # Normalize all values to 0-100 scale for consistent comparison
    normalized_values = []
    for col in valid_columns:
        col_min, col_max = df[col].min(), df[col].max()
        if col_max != col_min:
            # Standard min-max normalization scaled to 0-100
            normalized_val = ((mean_values[col] - col_min) / (col_max - col_min)) * 100
        else:
            # Handle edge case where all values are identical
            normalized_val = 50  # Default to middle of scale
        normalized_values.append(normalized_val)
    
    fig = go.Figure()
    
    # Create the radar chart trace
    fig.add_trace(go.Scatterpolar(
        r=normalized_values + [normalized_values[0]],  # Close the polygon by repeating first value
        theta=valid_columns + [valid_columns[0]],      # Close the polygon by repeating first column
        fill='toself',          # Fill the enclosed area
        name='Data Profile',    # Legend label
        line_color='#0083B8'    # Consistent blue color scheme
    ))
    
    # Configure chart layout with polar coordinates
    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,     # Show radial grid lines
                range=[0, 100]    # Fixed scale for all variables
            )),
        title="Radar Chart - Data Profile",
        paper_bgcolor='rgba(0,0,0,0)',  # Transparent background
        font={'color': 'white'}          # White text for dark theme
    )
    
    return {'fig': fig}