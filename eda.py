import streamlit as st
from streamlit_option_menu import option_menu
import pandas as pd
import matplotlib.pyplot as plt


def EDA(uploaded_file):
    st.title("Explanatory Data Analysis")
    st.write("Welcome to Explanatory Data Analysis Page!")

    df = uploaded_file

    # Store the original DataFrame in session state
    if "original_df" not in st.session_state:
        st.session_state.original_df = df.copy()

    # Store the current DataFrame in session state
    if "df" not in st.session_state:
        st.session_state.df = df.copy()

    # Create a checkbox in the sidebar
    checkbox = st.checkbox("Show data")
    bar = st.checkbox("Bar Graph")
    line = st.checkbox("Line Graph")
    # If the checkbox is ticked, display the DataFrame
    if checkbox:
        st.write(st.session_state.df)
    elif bar:
        fig, ax = plt.subplots()
        X_axis = st.selectbox(
            label="X-axis", options=["None"] + st.session_state.df.columns.tolist()
        )
        y_axis_option = st.selectbox(label="Y-axis", options=["value_counts"])

        if y_axis_option == "value_counts":
            count = st.session_state.df[X_axis].value_counts()
            ax.bar(count.index, count.values, color="maroon", width=0.4)
            ax.set_ylabel("Counts")
        else:
            ax.bar(
                st.session_state.df[X_axis],
                st.session_state.df[y_axis_option],
                color="maroon",
                width=0.4,
            )
            ax.set_ylabel(y_axis_option)
        ax.set_xlabel(X_axis)
        ax.set_title(f"{y_axis_option} for {X_axis}")
        st.pyplot(fig)

    elif line:
        fig, ax = plt.subplots()
        X_axis = st.selectbox(
            label="X-axis", options=["None"] + st.session_state.df.columns.tolist()
        )
        y_axis_option = st.selectbox(label="Y-axis", options=["value_counts"])

        if y_axis_option == "value_counts":
            count = st.session_state.df[X_axis].value_counts()
            ax.plot(count.index, count.values, marker="o")
            ax.set_ylabel("Counts")
        else:
            ax.plot(
                st.session_state.df[X_axis],
                st.session_state.df[y_axis_option],
                marker="o",
            )
            ax.set_ylabel(y_axis_option)

        ax.set_xlabel(X_axis)
        ax.set_title(f"{y_axis_option} for {X_axis}")

        st.pyplot(fig)
    # elif uploaded_file is None:
    #     st.write("Please Upload the CSV File in the Home Page to get started")
