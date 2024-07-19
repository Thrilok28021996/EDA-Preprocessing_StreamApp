"""
This module contains functions for data preprocessing using Streamlit.
It provides a user interface for selecting columns, replacing values, and filtering data.
"""

import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu


def choose_columns(df):
    """Function to choose columns in the data."""
    st.subheader("Select Columns")
    columns = st.multiselect(
        label="Choose columns to keep",
        options=df.columns.tolist(),
    )
    if columns:
        df = df[columns]
        st.success(f"Selected {len(columns)} columns")
    return df


def replace_values(df):
    """Function to Replace values in the data."""
    st.subheader("Replace Values")
    col1, col2 = st.columns(2)
    with col1:
        column_to_edit = st.selectbox("Select Column to Edit", df.columns)
    with col2:
        current_value = st.selectbox(
            "Select value to replace",
            df[column_to_edit].unique(),
        )
    new_value = st.text_input("Enter new value")

    if st.button("Replace", key="replace_button"):
        df[column_to_edit] = df[column_to_edit].replace(current_value, new_value)
        st.success(
            f"Replaced '{current_value}' with '{new_value}' in column '{column_to_edit}'"
        )

    return df


def filter_data_ui(df):
    """Function to filter the data."""
    st.subheader("Filter Data")
    if "filters" not in st.session_state:
        st.session_state.filters = []

    col1, col2 = st.columns(2)
    with col1:
        if st.button("Add Filter", key="add_filter"):
            st.session_state.filters.append({})
    with col2:
        if st.button("Remove Filter", key="remove_filter") and st.session_state.filters:
            st.session_state.filters.pop()

    for i, _ in enumerate(st.session_state.filters):
        st.markdown(f"**Filter {i+1}**")
        col1, col2 = st.columns(2)
        with col1:
            column = st.selectbox(
                "Filter column",
                options=["All"] + df.columns.tolist(),
                key=f"column_{i}",
            )
        with col2:
            if column != "All":
                value = st.selectbox(
                    f"Select value for {column}",
                    options=["All"] + df[column].unique().tolist(),
                    key=f"value_{i}",
                )
                df = filter_data(column, value, df)

    return df


def preprocessing(uploaded_file):
    """Function for preprocessing the Data."""
    st.title("Data Preprocessing")
    st.write("Welcome to the Preprocessing Page!")

    if uploaded_file is not None:
        df = uploaded_file

        # Create a stylish sidebar menu
        with st.sidebar:
            selected = option_menu(
                menu_title="Preprocessing Options",
                options=["Choose Columns", "Replace Values", "Filter Data"],
                icons=["columns", "pencil-square", "funnel"],
                menu_icon="gear",
                default_index=0,
                styles={
                    "container": {
                        "padding": "0!important",
                        "background-color": "#f0f2f6",
                    },
                    "icon": {"color": "#0083B8", "font-size": "25px"},
                    "nav-link": {
                        "font-size": "16px",
                        "text-align": "left",
                        "margin": "0px",
                        "--hover-color": "#e6f0ff",
                    },
                    "nav-link-selected": {"background-color": "#0083B8"},
                },
            )

        # Store the original DataFrame in session state
        if "original_df" not in st.session_state:
            st.session_state.original_df = df.copy()

        # Store the current DataFrame in session state
        if "df" not in st.session_state:
            st.session_state.df = df.copy()

        # Create a checkbox to show/hide data
        show_data = st.checkbox("Show data", value=True)
        if show_data:
            st.write(st.session_state.df)

        # Render the selected page
        if selected == "Choose Columns":
            st.session_state.df = choose_columns(st.session_state.df)
        elif selected == "Replace Values":
            st.session_state.df = replace_values(st.session_state.df)
        elif selected == "Filter Data":
            st.session_state.df = filter_data_ui(st.session_state.df)

        st.write(st.session_state.df)

    else:
        st.warning("Please upload a CSV file on the Home Page to get started")
