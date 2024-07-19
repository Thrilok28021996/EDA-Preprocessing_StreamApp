import pandas as pd
import streamlit as st
from streamlit_option_menu import option_menu


def filter_data(column, value, df):
    """Function to filter the data."""
    if column != "All" and value != "All":
        return df[df[column] == value]
    return df.copy()


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
            st.subheader("Select Columns")
            columns = st.multiselect(
                label="Choose columns to keep",
                options=st.session_state.df.columns.tolist(),
            )
            if columns:
                st.session_state.df = st.session_state.df[columns]
                st.success(f"Selected {len(columns)} columns")
                st.write(st.session_state.df)

        elif selected == "Replace Values":
            st.subheader("Replace Values")
            col1, col2 = st.columns(2)
            with col1:
                column_to_edit = st.selectbox(
                    "Select Column to Edit", st.session_state.df.columns
                )
            with col2:
                current_value = st.selectbox(
                    "Select value to replace",
                    st.session_state.df[column_to_edit].unique(),
                )
            new_value = st.text_input("Enter new value")

            if st.button("Replace", key="replace_button"):
                st.session_state.df[column_to_edit] = st.session_state.df[
                    column_to_edit
                ].replace(current_value, new_value)
                st.success(
                    f"Replaced '{current_value}' with '{new_value}' in column '{column_to_edit}'"
                )
                st.write(st.session_state.df)

            if st.button("Reset to Original", key="reset_button"):
                st.session_state.df = st.session_state.original_df.copy()
                st.success("DataFrame reset to original values")
                st.write(st.session_state.df)

        elif selected == "Filter Data":
            st.subheader("Filter Data")
            if "filters" not in st.session_state:
                st.session_state.filters = []

            col1, col2 = st.columns(2)
            with col1:
                if st.button("Add Filter", key="add_filter"):
                    st.session_state.filters.append({})
            with col2:
                if (
                    st.button("Remove Filter", key="remove_filter")
                    and st.session_state.filters
                ):
                    st.session_state.filters.pop()

            filtered_df = st.session_state.df

            for i, filter_dict in enumerate(st.session_state.filters):
                st.markdown(f"**Filter {i+1}**")
                col1, col2 = st.columns(2)
                with col1:
                    column = st.selectbox(
                        "Filter column",
                        options=["All"] + filtered_df.columns.tolist(),
                        key=f"column_{i}",
                    )
                with col2:
                    if column != "All":
                        value = st.selectbox(
                            f"Select value for {column}",
                            options=["All"] +
                            filtered_df[column].unique().tolist(),
                            key=f"value_{i}",
                        )
                        filtered_df = filter_data(column, value, filtered_df)

            st.session_state.df = filtered_df
            st.write(st.session_state.df)

    else:
        st.warning("Please upload a CSV file on the Home Page to get started")
