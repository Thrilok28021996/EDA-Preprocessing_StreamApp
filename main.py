import streamlit as st


def home():
    st.title("Welcome to EDA and Preprocessing 🙏🏼")


def upload_csv():
    # Sidebar for file upload
    st.title("Upload your CSV file To Get Started")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")
    return uploaded_file
