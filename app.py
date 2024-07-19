"""
This App.py File has code related to Home page.
Such as Different Functionalities to access the different options to choose from.
"""

import streamlit as st
from streamlit_option_menu import option_menu

from constant import info
from eda import explanatory_data_analysis
from feedback import feedback
from main import home, upload_csv
from preprocessing import preprocessing
from utils import process_uploaded_file

st.set_page_config(page_title="EDA and Preprocessing",
                   page_icon="🧑‍💻", layout="wide")
# Add custom CSS
st.markdown(
    """
        <style>
        .stApp {
            background-color: black;
        }
        .stButton>button {
            background-color: #0083B8;
            color: white;
        }
        .stSelectbox {
            background-color: white;
        }
        </style>
    """,
    unsafe_allow_html=True,
)

with st.sidebar:
    # Create an option menu for navigation
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "EDA", "Preprocessing", "Feedback"],
        icons=["house", "file", "file", "file"],
        menu_icon="cast",
        default_index=0,
        # orientation="horizontal",
        orientation="vertical",
        styles={
            "container": {"padding": "0!important", "background-color": "#f4d1a4"},
            "icon": {"color": "orange", "font-size": "25px"},
            "nav-link": {
                "font-size": "16px",
                "text-align": "left",
                "margin": "1px",
                "--hover-color": "#faebd7",
            },
            "nav-link-selected": {"background-color": "green"},
        },
    )


# Initialize the session state if it doesn't exist
if "df" not in st.session_state:
    st.session_state.df = None

# Render the selected page
if selected == "Home":
    home()
    uploaded_file = upload_csv()
    if uploaded_file is not None:
        df = process_uploaded_file(uploaded_file)
        st.session_state.df = df

elif selected == "EDA":
    if st.session_state.df is not None:
        explanatory_data_analysis(st.session_state.df)
    else:
        st.warning("Please Upload the CSV File in the Home Page to get started.")
elif selected == "Preprocessing":
    if st.session_state.df is not None:
        preprocessing(st.session_state.df)
    else:
        st.warning("Please Upload the CSV File in the Home Page to get started.")

elif selected == "Feedback":
    if st.session_state.df is not None:
        feedback(info)
    else:
        st.warning(
            """Please Upload the CSV File in the Home Page to get started.\n
            Once you have used the app. Please provide the feedback here."""
        )
