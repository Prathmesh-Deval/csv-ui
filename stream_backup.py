import streamlit as st
import pandas as pd
import os
import sqlite3
from sqlalchemy import create_engine

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

        /* Button in the top-right corner */
        .top-right-button {
            position: absolute;
            top: 10px;
            right: 10px;
            z-index: 1000;
        }

        /* Chatbox UI styles */
        .chat-box {
            width: 100%;
            max-width: 800px;
            margin: 0 auto;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            height: 500px;
            overflow-y: auto;
        }

        .chat-input {
            width: 100%;
            margin-top: 20px;
            display: flex;
        }

        .chat-input input {
            flex-grow: 1;
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            margin-right: 10px;
        }

        .chat-input button {
            padding: 10px;
            border: 1px solid #ccc;
            border-radius: 8px;
            background-color: #4CAF50;
            color: white;
            cursor: pointer;
        }
    </style>
"""

st.markdown(custom_css, unsafe_allow_html=True)


# Function to load CSV and generate insights
def load_file(file):
    try:
        # Save the uploaded file to the 'uploads' directory
        file_path = os.path.join("../uploads", file.name)
        os.makedirs("../uploads", exist_ok=True)  # Create the uploads directory if it doesn't exist

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
    # Save updated CSV to the uploads folder
    file_path = os.path.join("../uploads", file_name)
    df.to_csv(file_path, index=False)
    return file_path


# Function to convert DataFrame to SQLite database
def df_to_sql(df):
    # Create an in-memory SQLite database
    conn = sqlite3.connect(':memory:')
    # Save the dataframe to SQL
    df.to_sql('data', conn, index=False, if_exists='replace')
    # Now we back it up to a file
    file_db = sqlite3.connect('../DATABASE.db')
    print("DB CREATED")
    conn.backup(file_db)
    file_db.close()
    conn.close()
    return 'DATABASE.db'


# Streamlit App Structure
def main():
    # Check if the user is in chat mode
    if getattr(st.session_state, "chat_mode", False):
        st.title("Chat with Your Database")

        # Chat interface layout
        st.markdown('<div class="chat-box">', unsafe_allow_html=True)

        if 'messages' not in st.session_state:
            st.session_state.messages = []

        # Display the conversation
        for msg in st.session_state.messages:
            st.markdown(f"**{msg['role']}:** {msg['content']}")

        st.markdown('</div>', unsafe_allow_html=True)

        # Input field for the user message
        with st.form(key="chat_input_form"):
            user_input = st.text_input("What's on your mind?", key="user_input", placeholder="Ask something...")
            submit_button = st.form_submit_button(label="Send")

        if submit_button and user_input:
            # Add user message to the conversation
            st.session_state.messages.append({"role": "User", "content": user_input})

            # Here you can add your LLM or chatbot backend to respond.
            # For now, we simulate a response.
            st.session_state.messages.append({"role": "Chatbot", "content": f"Simulated response to: {user_input}"})

            # Rerun to update chat history
            st.rerun()

    else:
        # Add button for "Start Chat" in top-right corner
        start_chat_button = st.button("Start Chat", key="start_chat", help="Start Chat with your database")

        # Check if user clicked "Start Chat"
        if start_chat_button:
            st.session_state.chat_mode = True
            st.session_state.df_for_sql = st.session_state.df  # Store the current df to convert to SQL
            df_to_sql(st.session_state.df)  # Convert current df to SQL
            st.rerun()  # Use st.rerun() if you're using Streamlit >=1.18

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

                # Create a container for the column names and descriptions
                st.subheader("Edit Column Names and Descriptions")

                # Display the header for the columns (existing column name, new column name, description)
                col1, col2, col3 = st.columns([3, 3, 4])  # Adjust width for better alignment
                col1.write("**Existing Column Name**")
                col2.write("**New Column Name**")
                col3.write("**Description**")

                # Create a loop for editing column names and descriptions
                for i, col in enumerate(updated_column_names):
                    with st.container():
                        col1, col2, col3 = st.columns([2, 2, 3])  # Adjust width for better alignment
                        with col1:
                            st.write(col)  # Display existing column name
                        with col2:
                            new_name = st.text_input(f"1", value=col, key=f"col_{i}", label_visibility="collapsed")
                            updated_column_names[i] = new_name  # Update the name in the list
                        with col3:
                            description = st.text_input(f"Description {i + 1}", key=f"desc_{i}",label_visibility="collapsed")  # Description input

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
