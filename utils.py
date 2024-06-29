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

# Function to save feedback to a CSV file
def save_feedback(feedback_data):
    feedback_file = 'feedback.csv'
    feedback_df = pd.DataFrame([feedback_data])
    if os.path.exists(feedback_file):
        feedback_df.to_csv(feedback_file, mode='a', header=False, index=False)
    else:
        feedback_df.to_csv(feedback_file, mode='w', header=True, index=False)
        # Git commands to add, commit, and push the CSV file
    subprocess.run(['git', 'add', feedback_file])
    subprocess.run(['git', 'commit', '-m', 'Update feedback'])
    subprocess.run(['git', 'push'])
