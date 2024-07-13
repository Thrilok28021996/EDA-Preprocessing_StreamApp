import streamlit as st
from streamlit_option_menu import option_menu


def filter_data(column, a, df):
    """Function To filter the data."""
    if column != "All":
        data = df[df[column] == a]
    elif column == "All":
        data = df.copy()
    return data


def preprocessing(uploaded_file):
    """Function for preprocessing the Data."""
    st.title("Preprocessing")
    st.write("Welcome to Preprocessing Page!")

    if uploaded_file is not None:
        selected = option_menu(
            menu_title="preprocessing",
            options=["Choose", "Replace", "Filter"],
            icons=["house", "file", "gear"],
            menu_icon="cast",
            default_index=0,
            orientation="horizontal",
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
        df = uploaded_file

        # Store the original DataFrame in session state
        if "original_df" not in st.session_state:
            st.session_state.original_df = df.copy()

        # Store the current DataFrame in session state
        if "df" not in st.session_state:
            st.session_state.df = df.copy()

        # Create a checkbox in the sidebar
        checkbox = st.checkbox("Show data")
        # If the checkbox is ticked, display the DataFrame
        if checkbox:
            st.write(st.session_state.df)

        # Render the selected page
        if selected == "Choose":
            columns = st.multiselect(
                label="Select columns", options=st.session_state.df.columns.tolist()
            )
            if columns:
                st.session_state.df = st.session_state.df[columns]
                st.write(st.session_state.df)

        elif selected == "Replace":
            st.title("Replace Values in DataFrame")
            # Select column
            column_to_edit = st.selectbox(
                "Select Column to Edit", st.session_state.df.columns
            )

            # Enter current value
            current_value = st.selectbox(
                "Select value to replace", st.session_state.df[column_to_edit].unique()
            )

            # Enter new value
            new_value = st.text_input("New Value")

            # Button to replace values
            if st.button("Replace"):
                # Perform the replacement
                st.session_state.df[column_to_edit] = st.session_state.df[
                    column_to_edit
                ].replace(current_value, new_value)
                st.success(
                    f"Replaced '{current_value}' with '{new_value}' in column '{column_to_edit}'"
                )
                # Display the updated DataFrame
                st.write(st.session_state.df)

            # Button to reset to original values
            if st.button("Reset to Original"):
                st.session_state.df = st.session_state.original_df.copy()
                st.success("DataFrame reset to original values")
                st.write(st.session_state.df)

        elif selected == "Filter":
            st.title("Filter the Columns in dataframe")
            # Initialize session state
            if "num_filters" not in st.session_state:
                st.session_state.num_filters = 0
            if "filters" not in st.session_state:
                st.session_state.filters = []

            # Button to add filters
            if st.button("Add Filter"):
                st.session_state.num_filters += 1
                st.session_state.filters.append({"use_previous": False})

            if st.button("Remove Filter") and st.session_state.num_filters > 0:
                st.session_state.num_filters -= 1
                st.session_state.filters.pop()

            # Generate filters dynamically
            for i in range(st.session_state.num_filters):
                st.text("Filter:", {i + 1})
                use_previous = st.checkbox(
                    f"Use previous filter for next filter ", key=f"use_previous_{i}"
                )
                st.session_state.filters[i]["use_previous"] = use_previous

                if use_previous and i > 0:
                    previous_filter = st.session_state.filters[i - 1]
                    filtered_df = st.session_state.df
                    b = st.text_input("Your name", key="name2")
                else:
                    filtered_df = st.session_state.df

                name_filter = f"name{i}"
                column = st.text_input("Filter column", key=name_filter)
                st.write(column)
                a = st.selectbox(
                    f"Select Filter {column}",
                    options=["All"] + filtered_df[column].unique().tolist(),
                    key=f"type_{i}",
                )
                st.write(a)
                st.session_state.filters[i][column] = a
                st.session_state.df = filter_data(column, a, st.session_state.df)
                st.write(st.session_state.df)
    else:
        st.write("Please Upload the CSV File in the Home Page to get started")
