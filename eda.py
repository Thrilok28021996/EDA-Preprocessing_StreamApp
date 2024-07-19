import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from matplotlib import colors

from utils import (
    check_data_types,
    check_missing_values,
    detect_outliers,
    find_duplicates,
)


def explanatory_data_analysis(uploaded_file):
    """Function that has code for Explanatory data analysis."""
    st.title("Explanatory Data Analysis")
    st.write("Welcome to Explanatory Data Analysis Page!")

    df = uploaded_file

    # Store the original DataFrame in session state
    if "original_df" not in st.session_state:
        st.session_state.original_df = df.copy()

    # Store the current DataFrame in session state
    if "df" not in st.session_state:
        st.session_state.df = df.copy()

    # Create checkboxes for different analysis options
    analysis_options = {
        "Show data": st.checkbox("Show data"),
        "Bar Graph": st.checkbox("Bar Graph"),
        "Line Graph": st.checkbox("Line Graph"),
        "Histogram": st.checkbox("Histogram"),
        "Pie Graph": st.checkbox("Pie Graph"),
        "Scatter Graph": st.checkbox("Scatter Graph"),
        "Box Graph": st.checkbox("Box Graph"),
        "Heatmap": st.checkbox("Heatmap"),
        "Area Graph": st.checkbox("Area Graph"),
        "Find Duplicates": st.checkbox("Find Duplicates in the data"),
        "Find Missing data": st.checkbox("Find Missing data"),
        "Find Outliers": st.checkbox("Find Outliers in data wrt column"),
        "Print Data types": st.checkbox("Print the Data types of the columns"),
    }

    # Handle each analysis option
    for option, checked in analysis_options.items():
        if checked:
            handle_analysis_option(option, st.session_state.df)


def handle_analysis_option(option, df):
    """Handle different analysis options."""
    if option == "Show data":
        st.write(df)
    elif option == "Bar Graph":
        plot_bar_graph(df)
    elif option == "Line Graph":
        plot_line_graph(df)
    elif option == "Histogram":
        plot_histogram(df)
    elif option == "Pie Graph":
        plot_pie_graph(df)
    elif option == "Scatter Graph":
        plot_scatter_graph(df)
    elif option == "Box Graph":
        plot_box_graph(df)
    elif option == "Heatmap":
        plot_heatmap(df)
    elif option == "Area Graph":
        plot_area_graph(df)
    elif option == "Find Duplicates":
        find_duplicates(df)
    elif option == "Find Missing data":
        check_missing_values(df)
    elif option == "Find Outliers":
        detect_outliers_in_column(df)
    elif option == "Print Data types":
        check_data_types(df)


def plot_bar_graph(df):
    """Plot a bar graph."""
    fig, ax = plt.subplots()
    x_axis = st.selectbox("X-axis", options=df.columns.tolist())
    count = df[x_axis].value_counts()
    ax.bar(count.index, count.values, color="maroon", width=0.4)
    ax.set_xlabel(x_axis)
    ax.set_ylabel("Counts")
    ax.set_title(f"Value counts for {x_axis}")
    st.pyplot(fig)


def plot_line_graph(df):
    """Plot a line graph."""
    fig, ax = plt.subplots()
    x_axis = st.selectbox("X-axis", options=df.columns.tolist())
    count = df[x_axis].value_counts()
    ax.plot(count.index, count.values, marker="o")
    ax.set_xlabel(x_axis)
    ax.set_ylabel("Counts")
    ax.set_title(f"Value counts for {x_axis}")
    st.pyplot(fig)


def plot_histogram(df):
    """Plot a histogram."""
    column = st.selectbox("Column", options=df.columns.tolist())
    plt.hist(df[column])
    st.pyplot(plt)


def plot_pie_graph(df):
    """Plot a pie graph."""
    column = st.selectbox("Column", options=df.columns.tolist())
    count = df[column].value_counts()
    fig, ax = plt.subplots()
    ax.pie(count.values, labels=count.index.tolist(), autopct="%1.1f%%")
    ax.set_title(f"Pie chart for {column}")
    st.pyplot(fig)


def plot_scatter_graph(df):
    """Plot a scatter graph."""
    x_axis = st.selectbox("X-axis", options=df.columns.tolist())
    y_axis = st.selectbox("Y-axis", options=df.columns.tolist())
    st.scatter_chart(df, x=x_axis, y=y_axis)


def plot_box_graph(df):
    """Plot a box graph."""
    column = st.selectbox("Column", options=df.columns.tolist())
    fig, ax = plt.subplots()
    ax.boxplot(df[column].dropna())
    ax.set_title(f"Box plot for {column}")
    st.pyplot(fig)


def plot_heatmap(df):
    """Plot a heatmap."""
    columns = st.multiselect("Select columns", options=df.columns.tolist())
    if columns:
        corr_matrix = df[columns].corr()
        fig, ax = plt.subplots()
        im = ax.imshow(corr_matrix, cmap="coolwarm")
        ax.set_xticks(np.arange(len(columns)))
        ax.set_yticks(np.arange(len(columns)))
        ax.set_xticklabels(columns)
        ax.set_yticklabels(columns)
        plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")
        for i in range(len(columns)):
            for j in range(len(columns)):
                text = ax.text(
                    j,
                    i,
                    f"{corr_matrix.iloc[i, j]:.2f}",
                    ha="center",
                    va="center",
                    color="w",
                )
        ax.set_title("Correlation Heatmap")
        fig.tight_layout()
        st.pyplot(fig)


def plot_area_graph(df):
    """Plot an area graph."""
    x_axis = st.selectbox("X-axis", options=df.columns.tolist())
    y_axis = st.selectbox("Y-axis", options=df.columns.tolist())
    st.area_chart(df, x=x_axis, y=y_axis)


def detect_outliers_in_column(df):
    """Detect outliers in a specific column."""
    columns = st.selectbox(
        "Select column",
        options=df.select_dtypes(include=[np.number]).columns.tolist(),
    )
    detect_outliers(df, columns)
