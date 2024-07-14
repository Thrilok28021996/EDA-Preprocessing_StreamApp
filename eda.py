"""
This App.py File has code related to Home page. 
Such as Different Functionalities to access the different options to choose from.
"""

import streamlit as st
import matplotlib.pyplot as plt
from matplotlib import colors
import numpy as np
from utils import (
    check_missing_values,
    find_duplicates,
    detect_outliers,
    check_data_types,
)


def explanatory_data_analysis(uploaded_file):
    """Function that has code for Explanatory data analysis."""
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
    bar_graph = st.checkbox("Bar Graph")
    line = st.checkbox("Line Graph")
    hist = st.checkbox("Histogram")
    pie = st.checkbox("Pie Graph")
    scatter = st.checkbox("Scatter Graph")
    box = st.checkbox("Box Graph")
    heatmap = st.checkbox("Heatmap")
    area = st.checkbox("Area Graph")
    duplicates = st.checkbox("Find Duplicates in the data")
    missing_values_check = st.checkbox("Find Missing data")
    outliers = st.checkbox("Find Outliers in data wrt column")
    data_type = st.checkbox("Print the Data types of the columns")

    # If the checkbox is ticked, display the DataFrame
    if checkbox:
        st.write(st.session_state.df)
    elif bar_graph:
        fig, ax = plt.subplots()
        x_axis = st.selectbox(
            label="X-axis", options=st.session_state.df.columns.tolist()
        )
        y_axis_option = st.selectbox(
            label="Y-axis",
            options=[
                "value_counts",
            ],
        )

        if y_axis_option == "value_counts":
            count = st.session_state.df[x_axis].value_counts()
            ax.bar(count.index, count.values, color="maroon", width=0.4)
            ax.set_ylabel("Counts")
        else:
            ax.bar(
                st.session_state.df[x_axis],
                st.session_state.df[y_axis_option],
                color="maroon",
                width=0.4,
            )
            ax.set_ylabel(y_axis_option)
        ax.set_xlabel(x_axis)
        ax.set_title(f"{y_axis_option} for {x_axis}")
        st.pyplot(fig)

    elif line:
        fig, ax = plt.subplots()
        x_axis = st.selectbox(
            label="X-axis", options=st.session_state.df.columns.tolist()
        )
        y_axis_option = st.selectbox(label="Y-axis", options=["value_counts"])

        if y_axis_option == "value_counts":
            count = st.session_state.df[x_axis].value_counts()
            ax.plot(count.index, count.values, marker="o")
            ax.set_ylabel("Counts")
        else:
            ax.plot(
                st.session_state.df[x_axis],
                st.session_state.df[y_axis_option],
                marker="o",
            )
            ax.set_ylabel(y_axis_option)

        ax.set_xlabel(x_axis)
        ax.set_title(f"{y_axis_option} for {x_axis}")
        st.pyplot(fig)

    elif hist:
        column = st.selectbox(
            label="Column", options=st.session_state.df.columns.tolist()
        )
        plt.hist(st.session_state.df[column])
        st.pyplot(plt)

    elif pie:
        column = st.selectbox(
            label="Column", options=st.session_state.df.columns.tolist()
        )
        count = st.session_state.df[column].value_counts()
        fig = plt.figure(figsize=(10, 7))
        plt.pie(count.values, labels=count.index.tolist())
        st.pyplot(plt)

    elif scatter:
        st.write("Choose the columns to plot")
        x_axis = st.selectbox(
            label="X-axis", options=st.session_state.df.columns.tolist()
        )
        y_axis = st.selectbox(
            label="Y-axis", options=st.session_state.df.columns.tolist()
        )
        st.scatter_chart(
            st.session_state.df,
            x=x_axis,
            y=y_axis,
        )
    elif box:
        column = st.selectbox(
            label="Column", options=st.session_state.df.columns.tolist()
        )
        count = st.session_state.df[column].value_counts()
        fig = plt.figure(figsize=(10, 7))
        plt.boxplot(count.values.tolist())
        st.pyplot(plt)

    elif heatmap:
        st.write("Choose the numerical columns")
        columns = st.multiselect(
            label="Select columns", options=st.session_state.df.columns.tolist()
        )
        corr_matrix = st.session_state.df[columns].corr()
        # Create a custom color
        # map with blue and green colors
        colors_list = ["#FF5733", "#FFC300"]
        cmap = colors.ListedColormap(colors_list)

        # Plot the heatmap with custom colors and annotations
        plt.imshow(corr_matrix, cmap=cmap, vmin=0, vmax=1, extent=[0, 5, 0, 5])
        for i in range(len(columns)):
            for j in range(len(columns)):
                plt.annotate(
                    str(round(corr_matrix.values[i][j], 2)),
                    xy=(j + 0.25, i + 0.7),
                    ha="center",
                    va="center",
                    color="white",
                )

        # Add colorbar
        cbar = plt.colorbar(ticks=[0, 0.5, 1])
        cbar.ax.set_yticklabels(["Low", "Medium", "High"])
        st.pyplot(plt)

    elif area:
        st.write("Choose the columns to plot")
        x_axis = st.selectbox(
            label="X-axis", options=st.session_state.df.columns[columns].tolist()
        )
        y_axis = st.selectbox(
            label="Y-axis", options=st.session_state.df.columns[columns].tolist()
        )

        st.area_chart(st.session_state.df, x=x_axis, y=y_axis)
    elif duplicates:
        find_duplicates(st.session_state.df)
    elif missing_values_check:
        check_missing_values(st.session_state.df)
    elif outliers:
        columns = st.selectbox(
            label="Select columns",
            options=st.session_state.df.select_dtypes(
                include=[np.number]
            ).columns.tolist(),
        )
        detect_outliers(st.session_state.df, columns)
    elif data_type:
        check_data_types(st.session_state.df)

    # elif uploaded_file is None:
    #     st.write("Please Upload the CSV File in the Home Page to get started")
