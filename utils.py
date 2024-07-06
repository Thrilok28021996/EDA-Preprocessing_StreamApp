import streamlit as st
import pandas as pd
import os
import subprocess


# Define a function to process and cache uploaded data
@st.cache_data
def process_uploaded_file(uploaded_file):
    if uploaded_file is not None:
        # Read the uploaded CSV file
        df = pd.read_csv(uploaded_file)
        return df
    return None
