import streamlit as st
from streamlit_option_menu import option_menu
from main import home, upload_csv
from eda import EDA
import pandas as pd
from preprocessing import preprocessing
from utils import process_uploaded_file, save_feedback
from streamlit_feedback import streamlit_feedback


with st.sidebar:
    # Create an option menu for navigation
    selected = option_menu(
        menu_title="Main Menu",
        options=["Home", "EDA", "Preprocessing","FeedBack"],
        icons=["house", "file","file", "gear"],
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


# Render the selected page
if selected == "Home":
    home()
    uploaded_file = upload_csv()
    if uploaded_file is not None:

        st.session_state.uploaded_file = uploaded_file

        st.session_state.df = process_uploaded_file(uploaded_file)

elif selected == "EDA":
    EDA(st.session_state.df)
elif selected == "Preprocessing":
    preprocessing(st.session_state.df)
elif selected == "FeedBack":
    # Add feedback collection point
    feedback = streamlit_feedback(
        feedback_type="faces",
        optional_text_label="[Optional] Please provide an explanation",
    )
    # st.write(feedback)
    # Save feedback if provided
    if feedback:
        feedback_data = {
            "feedback": feedback["score"],
            "optional_text": feedback["text"],
            "timestamp": pd.Timestamp.now(),
        }
        save_feedback(feedback_data)
        st.success("Thank you for your feedback!")
