import streamlit as st
import pandas as pd
import os

# Custom CSS to modify the layout and add the vertical separator
custom_css = """
    <style>
        /* Set the width of the app */
        .block-container {
            max-width: 100%;  /* Max width 100% */
            width: 100%;
        }

        /* Customize the file upload and insights section */
        .stFileUploader {
            width: 100%;  /* Ensure file uploader is wide enough */
        }

        .stTextInput>div>div>input {
            width: 100%;  /* Make the input fields use full width */
        }

        .stButton>button {
            width: 200px;  /* Make buttons wider */
        }

        .stDataFrame {
            width: 100%;  /* Ensure DataFrame takes up full available width */
        }

        /* Style for the separator line between 25% and 75% sections */
        .separator {
            border-left: 2px solid #ccc;
            background-color: white;
            height: 100vh;  /* Set to 100vh to fill the full height of the viewport */
            margin-top: 0;
        }

        /* Customizing the columns width */
        .left-column {
            width: 75%;
        }

        .right-column {
            width: 25%;
        }

        /* Apply padding for clarity */
        .left-column, .right-column {
            padding: 4px;
        }

        /* Center the header */
        .centered-header {
            text-align: center;
        }

        /* Style for the horizontal line */
        .separator-line {
            border: 0;
            height: 1px;
            background-color: white;
            margin-top: 10px;
            margin-bottom: 20px;
        }
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


# Function to load CSV and generate insights
def load_file(file):
    print("LOADING FILE ######################################")
    try:
        # Save the uploaded file to the 'uploads' directory
        file_path = os.path.join("uploads", file.name)
        os.makedirs("uploads", exist_ok=True)  # Create the uploads directory if it doesn't exist

        with open(file_path, "wb") as f:
            f.write(file.getbuffer())  # Save file to local storage

        # Check the file type and handle accordingly
        if file.name.endswith('.csv'):
            df = pd.read_csv(file_path)
        elif file.name.endswith(('.xls', '.xlsx')):  # Support Excel files
            df = pd.read_excel(file_path)  # Read Excel file
        else:
            st.error("Unsupported file format. Please upload a CSV or Excel file.")
            return None, None, None, None

        # Calculate insights
        file_size = os.path.getsize(file_path)
        column_info = df.dtypes.to_frame().reset_index()
        column_info.columns = ['Column Name', 'Data Type']
        column_info['Non-Null Count'] = df.notnull().sum().values
        column_info['Unique Count'] = df.nunique().values

        # Create a summary of the file
        insights = {
            "File Size (in bytes)": file_size,
            "Total Rows": len(df),
            "Total Columns": len(df.columns)
        }

        return insights, column_info, df, file_path

    except Exception as e:
        st.error(f"Error: {str(e)}")
        return None, None, None, None


# Function to save the updated CSV file
def save_csv(df, file_name):
    print("SAVING")
    # Save updated CSV to the uploads folder
    file_path = os.path.join("uploads", file_name)
    df.to_csv(file_path, index=False)
    return file_path


# Streamlit App Structure
def main():
    # Use HTML to center the title
    st.markdown("<h1 class='centered-header'>KKL CSV AI AGENT</h1>", unsafe_allow_html=True)

    # Add a horizontal separation line below the title in white
    st.markdown("<hr class='separator-line'>", unsafe_allow_html=True)

    # Create columns layout (75% and 25%)
    left_col, separator, right_col = st.columns([1, 0.01, 3])  # 75% for left, 25% for right

    # Left Column (75%): Upload File and CSV Insights
    with left_col:
        st.header("Upload File and CSV Insights")

        # File upload widget, support CSV and Excel files
        uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=["csv", "xls", "xlsx"])

        # Ensure file is loaded only once
        if uploaded_file is not None:
            # Only load the file if it's not already loaded
            if 'df' not in st.session_state:
                insights, column_info, df, file_path = load_file(uploaded_file)

                if df is not None:
                    # Store file data in session state for further use
                    st.session_state.df = df
                    st.session_state.insights = insights
                    st.session_state.column_info = column_info
                    st.session_state.file_path = file_path

                    # Notify user about successful file upload
                    st.success(f"File '{uploaded_file.name}' uploaded successfully.")

            else:
                # Use cached data if file is already loaded
                df = st.session_state.df
                insights = st.session_state.insights
                column_info = st.session_state.column_info
                file_path = st.session_state.file_path

            # Display file insights
            st.subheader("File Insights")
            st.write(insights)

            # Display basic file details
            st.write(f"File Size: {insights['File Size (in bytes)']} bytes")
            st.write(f"Total Rows: {insights['Total Rows']}")
            st.write(f"Total Columns: {insights['Total Columns']}")

    with separator:
        # Vertical separator between the left and right columns
        st.markdown("<div class='separator'></div>", unsafe_allow_html=True)

    # Right Column (75%): Edit Column Names, Column Insights, etc.
    with right_col:
        st.header("Update Column Names")

        # Checkbox to enable editing of column names
        enable_editing = st.checkbox("Review and edit column names", value=False)

        # Initialize the updated column names in session_state if not already initialized
        if 'updated_columns' not in st.session_state:
            st.session_state.updated_columns = list(df.columns)  # Initialize with original column names

        if enable_editing:
            updated_column_names = st.session_state.updated_columns  # Use the list stored in session_state

            columns_in_row = 3  # Set the number of columns per row
            columns = st.columns(columns_in_row)  # Divide the screen into columns

            # Create a loop for editing column names
            for i, col in enumerate(updated_column_names):
                # Determine which column to place the input in
                column_index = i % columns_in_row
                with columns[column_index]:
                    new_name = st.text_input(f"Column {i + 1}", value=col, key=f"col_{i}")
                    updated_column_names[i] = new_name  # Update the name in the list

            # Update the list stored in session state
            st.session_state.updated_columns = updated_column_names

            # Show a button to save changes
            if st.button("Save Changes"):
                # Apply the final column name changes to the DataFrame
                df.columns = updated_column_names
                save_path = save_csv(df, "updated_file.csv")
                st.success(f"Updated file saved at: {save_path}")

                # Use st.download_button to create a download link for the updated file
                with open(save_path, "rb") as f:
                    st.download_button(
                        label="Download Updated CSV",
                        data=f,
                        file_name="updated_file.csv",
                        mime="text/csv"
                    )

                # Show the updated dataframe
                st.dataframe(df)

        # Display Column Information in a table
        st.subheader("Original Column Insights")
        st.dataframe(column_info)

        # Display the original dataframe (truncated to first 10 rows)
        st.subheader("Data")
        st.dataframe(df.head())


# Run the app
if __name__ == "__main__":
    main()
