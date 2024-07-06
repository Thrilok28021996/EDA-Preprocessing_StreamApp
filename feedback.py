# from streamlit_feedback import streamlit_feedback
# import streamlit as st

# from utils import save_feedback
# import pandas as pd


# def feedback():  # Add feedback collection point
#     feedback = streamlit_feedback(
#         feedback_type="faces",
#         optional_text_label="[Optional] Please provide an explanation",
#     )
#     # st.write(feedback)
#     # Save feedback if provided
#     if feedback:
#         feedback_data = {
#             "feedback": feedback["score"],
#             "optional_text": feedback["text"],
#             "timestamp": pd.Timestamp.now(),
#         }
#         save_feedback(feedback_data)
#         st.success("Thank you for your feedback!")
