"""
This Utils.py File has code related to Utilizing the different functions. 

"""

import streamlit as st
import pandas as pd


# Define a function to process and cache uploaded data
@st.cache_data
def process_uploaded_file(uploaded_file):
    """Function."""
    if uploaded_file is not None:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)
        return df
    return None


def check_missing_values(df):
    """Function."""
    missing_data = df.isnull().sum()
    st.write("Missing data:")
    st.dataframe(missing_data)


def find_duplicates(df):
    """Function."""
    duplicated_rows = df.duplicated().any()
    if duplicated_rows:
        st.write("Duplicates found:", df[df.duplicated()])
    else:
        st.write("No duplicates found.")


def detect_outliers(df, column_name):
    """Function."""
    # Implement outlier detection logic using IQR
    q1 = df[column_name].quantile(0.25)
    q3 = df[column_name].quantile(0.75)
    # Finally, the IQR is calculated as Q3 - Q1
    iqr = q3 - q1
    lower_bound = q1 - 1.5 * iqr
    upper_bound = q3 + 1.5 * iqr
    lower_bound_outliers = df[df[column_name] < lower_bound]
    upper_bound_outliers = df[df[column_name] > upper_bound]
    st.write("Lower bound", lower_bound)
    st.write("Length  of Lower bound outliers", len(lower_bound_outliers))
    st.write("Lower bound outliers", lower_bound_outliers)
    st.write("Upper bound", upper_bound)
    st.write("Length  of Upper Bound Outliers", len(upper_bound_outliers))
    st.write("Upper Bound Outliers", upper_bound_outliers)


def check_data_types(df):
    """Function."""
    dtypes_df = df.dtypes
    dtypes_df.columns = ["Column", "Data Type"]
    st.write("Data types:")
    st.dataframe(dtypes_df)
