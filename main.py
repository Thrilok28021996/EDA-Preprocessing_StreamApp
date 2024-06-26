import streamlit as st


def home():
    st.title("Welcome to EDA and Preprocessing 🙏🏼")


def upload_csv():
    # Initialize session state

    if 'uploaded_file' not in st.session_state:
        st.session_state.uploaded_file = None

    if 'df' not in st.session_state:
        st.session_state.df = None
    # Sidebar for file upload
    st.title("Upload your CSV file To Get Started")
    uploaded_file = st.file_uploader("Upload a CSV file", type="csv")

    return uploaded_file
