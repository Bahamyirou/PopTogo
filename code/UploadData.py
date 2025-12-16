import os
import streamlit as st
import pandas as pd

from utils import (
    FETCH_WW_TRENDS_QUERY,
    get_cursor,
 
)


# pages/2_Upload_Data.py


# Set the page title and add a header
st.set_page_config(page_title="Upload your Trend Data", layout="wide")
st.markdown(
    """
## The uploaded file must contain at least the following columns: Location, Assay, Intensity, and Trend. 

Steps performed when you upload a file:

1. Once uploaded, your dataset is first displayed in a table for review. 
2. An inner merge is performed between your uploaded data and the existing trends in the SQL, based on the Location and Assay columns.
3. The merged dataset is then displayed below, with any differences highlighted for easy identification.

For any questions or issues, please contact the system administrator.
"""
)

# --- DEFINE YOUR COLUMN MAPPINGS HERE ---
# Use the format: {'Old Column Name': 'New Column Name'}
# Any column from the uploaded file not in this dictionary will keep its original name.
COLUMN_RENAME_MAP = {
    "Assay": "measure",
    "Intensity": "LatestLevel",
    "Trend": "latestTrends"
}

#  Define the list of columns you want to display
# IMPORTANT: Use the NEW, RENAMED column names from the map above.
COLUMNS_TO_DISPLAY = [
    "Location",
    "measure",
    "latestTrends",
    "LatestLevel"
]

# 1. Create the file uploader widget
# We allow both csv and xlsx file types.
uploaded_file = st.file_uploader(
    "Choose a csv file",
    type=['csv', 'xlsx'],
    help="Upload a CSV or Excel file to display its content."
)

# 2.  This block of code will only run if a file has been successfully uploaded.
if uploaded_file is not None:
    try:
        # 2. Check the file type and read it into a pandas DataFrame.
        # We store the dataframe in session state to persist it.
        if uploaded_file.name.endswith('.csv'):
            temp_df  = pd.read_csv(uploaded_file)
        else:
            temp_df  = pd.read_excel(uploaded_file)

        # --- RENAME THE COLUMNS ---
        # Apply the renaming map to the temporary dataframe
        renamed_df = temp_df.rename(columns=COLUMN_RENAME_MAP)

        existing_cols_to_display = [
            col for col in COLUMNS_TO_DISPLAY if col in renamed_df.columns
        ]
        # Create the final dataframe with only the selected columns
        final_df = renamed_df[existing_cols_to_display]

        # Store the FINAL, renamed dataframe in session state
        st.session_state.df_preview = final_df
            
        st.success("File uploaded successfully. Displaying preview below.")

    except Exception as e:
        # If any error occurs during file reading, show an error message.
        st.error(f"Error reading file: {e}")
        # Clear any old data from session state if the new file is invalid
        if 'df_preview' in st.session_state:
            del st.session_state.df_preview


# 3. Display the data table at the bottom of the page.
# This part checks if a valid dataframe exists in the session state before trying to show it.
if 'df_preview' in st.session_state:
    st.divider()
    st.header("Your uploaded Data Preview")
    st.dataframe(st.session_state.df_preview, use_container_width=True)
else:
    st.error(f"No file was uploaded...")


st.divider()

# ---  comparison ---
st.header("⚖️ SQL vs Local Trend — Inner Merge Comparison")

with st.spinner("Fetching database trends for comparison..."):
        if "df_ww" not in st.session_state:
            try:
                with get_cursor() as cursor:
                    cursor.execute(FETCH_WW_TRENDS_QUERY)
                    rows = [row.asDict() for row in cursor.fetchall()]
                    st.session_state.df_ww = pd.DataFrame(rows)
            except Exception as e:
                st.error(f"Failed to fetch database trends: {e}")
                # Stop execution of this block if fetching fails
                st.stop()
    
# Use the DataFrame from session state for the merge
if 'df_preview' in st.session_state:
     uploaded_data = st.session_state.df_preview.copy()
else:
    st.error(f"No file was uploaded...")
database_data = st.session_state.df_ww.copy()
# Select one column as a Series
database_data = database_data[['Location', 'measure', 'LatestLevel', 'Viral_Activity_Level', 'latestTrends']]

# --- Merge ---
try:
        # The key 'Location' is in COLUMNS_TO_DISPLAY, ensuring it exists in uploaded_data
    df_compare = pd.merge(
            uploaded_data,
            database_data,
            on=['Location', 'measure'],
            how='inner',
            suffixes=('_upload', '_database') # Clearer suffixes
    )

    df_compare = df_compare[['Location', 'measure',  'latestTrends_upload', 'latestTrends_database', 'LatestLevel_upload','LatestLevel_database', 'Viral_Activity_Level']]

    # --- Identify differences ---
    df_compare['TrendDiff'] = df_compare['latestTrends_upload'] != df_compare['latestTrends_database']
    df_compare['ViralDiff'] = df_compare['LatestLevel_upload'] != df_compare['LatestLevel_database']
    
    # --- Highlight function ---
    def highlight_differences(row):
      styles = []
      for col in df_compare.columns:
        if col.endswith('_upload'):
            base_col = col.replace('_upload', '_database')
            if row[col] != row[base_col]:
                styles.append('background-color: #ffcccc; font-weight: bold;')
            else:
                styles.append('')
        elif col.endswith('_database'):
            base_col = col.replace('_database', '_upload')
            if row[col] != row[base_col]:
                styles.append('background-color: #33ffff; font-weight: bold;')
            else:
                styles.append('')
        else:
            styles.append('')
      return styles
    
    #st.subheader("🧾 Detailed Comparison Table")

    st.write("Colors cells indicate where values differ between the two datasets.")

    # --- Render highlighted table ---
    st.dataframe(
       df_compare.style.apply(highlight_differences, axis=1),use_container_width=True
     )
    
except KeyError as e:
        st.error(f"Merge failed. Ensure both your uploaded file and the database contain the columns 'Location' and 'measure'. Missing key: {e}")
except Exception as e:
        st.error(f"An unexpected error occurred during the data merge: {e}")




#st.set_page_config(
 #   page_title="Upload Data Page",
 #   page_icon="📝",
 #   layout="wide",
 #   initial_sidebar_state="expanded",
#)
#st.title("📝 Upload Data Page")
#app()
