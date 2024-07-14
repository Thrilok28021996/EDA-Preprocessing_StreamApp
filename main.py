"""
This main.py File has code related to Home page. 
"""

import streamlit as st


def home():
    """Function to call the Title."""
    st.title("Welcome to EDA and Preprocessing 🙏🏼")


def upload_csv():
    """Function to upload the File."""
    st.title("Upload your CSV file To Get Started")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    return uploaded_file
