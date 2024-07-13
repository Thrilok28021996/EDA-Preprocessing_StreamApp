import streamlit as st
from streamlit_option_menu import option_menu
from main import home, upload_csv
from eda import explanatory_data_analysis
from preprocessing import preprocessing
from utils import process_uploaded_file


st.set_page_config(
    page_title="EDA and Preprocessing",
    page_icon="🧑‍💻",
)

with st.sidebar:
    # Create an option menu for navigation
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "EDA", "Preprocessing"],
        icons=["house", "file", "file"],
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
        st.write("Please Upload the CSV File in the Home Page to get started.")

elif selected == "Preprocessing":
    if st.session_state.df is not None:
        preprocessing(st.session_state.df)
    else:
        st.write("Please Upload the CSV File in the Home Page to get started.")


st.write("For any Queries or Feedback. Please mail to : altrathrill@gmail.com")
