import streamlit as st
import pandas as pd

from utils import (
    FETCH_MPOX_QUERY,
    UPDATE_MPOX_QUERY,
    INSERT_LOG_QUERY,
    INSERT_MPOX_QUERY,
    DELETE_MPOX_QUERY,
    can_user_edit,
    get_cursor,
    trigger_job_run,
    get_log_entry,
    get_username,
)


USER_CAN_EDIT = can_user_edit()

# Edit Data Form
@st.dialog("Change Row Data")
def edit_data_form(selected_indices):
    columns = ["Location", "EpiYear", "EpiWeek", "Week_start", "g2r_label"]

    edited_df = st.data_editor(
        st.session_state.df_mpox.iloc[selected_indices],
        column_order=columns,
        column_config={
            "g2r_label": st.column_config.SelectboxColumn(
                "g2r_label",
                options=[
                    "Consistent Detection",
                    "Intermittent Detection",
                    "No Detection",
                    "No Recent Data",
                ],
                required=True,
            ),
            "EpiYear": st.column_config.TextColumn(),
        },
        use_container_width=True,
        hide_index=True,
        disabled=("Location", "EpiYear", "EpiWeek", "Week_start"),
        key="edited_data_mpox",
    )

    if st.session_state.edited_data_mpox["edited_rows"] and st.button(
        "Submit", type="primary"
    ):
        with st.spinner('Submitting changes...'):
            log_entries = []
            for selected_index in selected_indices:
                with get_cursor() as cursor:
                    # Update SQL DB with the edited values
                    row = edited_df.loc[selected_index]
                    cursor.execute(
                        UPDATE_MPOX_QUERY,
                        {
                            "g2r_label": row["g2r_label"],
                            "location": row["Location"],
                            "epi_week": float(row["EpiWeek"]),
                            "epi_year": float(row["EpiYear"]),
                            "week_start": row["Week_start"],
                        },
                    )
                    # Update SQL DB with the log entry
                    cursor.execute(
                        INSERT_LOG_QUERY,
                        get_log_entry(
                            st.session_state.df_mpox.loc[selected_index],
                            edited_df.loc[selected_index],
                            "Mpox Trends",
                        ),
                    )
                    log_entries.append(
                        get_log_entry(
                            st.session_state.df_mpox.loc[selected_index],
                            edited_df.loc[selected_index],
                            "Mpox Trends",
                        )
                    )
                # Update local DataFrame with the edited values
                st.session_state.df_mpox.loc[selected_index, "g2r_label"] = edited_df.loc[
                    selected_index, "g2r_label"
                ]
            trigger_job_run("mpox", log_entries)

            st.session_state.show_success_toast = True
            print("dialog triggered re-render")
            st.rerun()

# Add New Raw Form
@st.dialog("Add New Row")
def add_new_row_form():
    st.write("Fill in all fields for a new row:")

    location = st.selectbox(
        "location",
        [
            "Select Location...",  # Placeholder to force selection
            "Calgary",
            "Edmonton",
            "Halifax",
            "Metro Vancouver",
            "Moncton",
            "Montreal",
            "Peel Region",
            "Regina",
            "St. John's",
            "Toronto",
            "Winnipeg",
        ],
        index=0,  # Start with placeholder selected
    )
    epi_year = st.number_input("EpiYear", min_value=2000, max_value=2100, value=None, step=1)
    epi_week = st.number_input("EpiWeek", min_value=1, max_value=53, value=None, step=1)
    week_start = st.date_input("Week_start", value=None, help="Format: YYYY-MM-DD")
    g2r_label = st.selectbox(
        "g2r_label",
        [
            "Select Label...",  # Placeholder to force selection
            "Consistent Detection",
            "Intermittent Detection",
            "No Detection",
            "No Recent Data",
        ],
        index=0,  # Start with placeholder selected
    )

    if st.button("Submit New Row", type="primary"):
        # Validate all fields are filled
        if not location or location == "Select Location...":
            st.warning("Please enter a location.")
            st.stop()

        if epi_year is None:
            st.warning("Please enter EpiYear.")
            st.stop()
        
        if epi_week is None:
            st.warning("Please enter EpiWeek.")
            st.stop()
        
        if week_start is None:
            st.warning("Please select Week_start.")
            st.stop()
        
        if not g2r_label or g2r_label == "Select Label...":
            st.warning("Please select g2r_label.")
            st.stop()
            
        # If all validations pass, proceed with submission    
        with st.spinner('Submitting new row...'):
            log_entries = []
            with get_cursor() as cursor:
                  # Update local DataFrame with new row 
                 new_row_df = pd.DataFrame([{
                   "Location": location,
                   "EpiYear": epi_year,
                   "EpiWeek": epi_week,
                   "Week_start": week_start.strftime("%Y-%m-%d"),
                   "g2r_label": g2r_label,
                 }])
                 cursor.execute(
                    INSERT_MPOX_QUERY,
                    {
                        "location": location,
                        "epi_year": int(epi_year),
                        "epi_week": int(epi_week),
                        "week_start": week_start.strftime("%Y-%m-%d"),
                        "g2r_label": g2r_label,
                    },
                )                
             
                # Update SQL DB with the log entry
                 cursor.execute(
                        INSERT_LOG_QUERY,
                        get_log_entry(
                             None,  # old_data
                             new_row_df.iloc[0],  # new_data
                             "Mpox Trends - Add New Row"
                          ),
                    )
                 log_entries.append(
                        get_log_entry(
                             None,  # old_data
                             new_row_df.iloc[0],  # new_data
                             "Mpox Trends - Add New Row"
                          )
                    ) 
          
            # Update local DataFrame with the edited values
            st.session_state.df_mpox = pd.concat(
                [st.session_state.df_mpox, new_row_df], ignore_index=True
            )
            # Log the new entry
            trigger_job_run("mpox", log_entries)

            st.session_state.show_success_toast = True
            print("dialog triggered re-render")
            st.rerun()

# Confirm Data Deletion Form
@st.dialog("Confirm Row Deletion")
def confirm_delete(selected_indices):
    st.warning("Are you sure you want to delete the selected row(s)? This action cannot be undone.")

    if st.button("Delete", type="primary"):
        log_entries = []
        with get_cursor() as cursor:
            for idx in selected_indices:
                row = st.session_state.df_mpox.iloc[idx]
                # You may also want to insert into log here
                cursor.execute(
                    DELETE_MPOX_QUERY,
                    {
                        "location": row["Location"],
                        "epi_year": float(row["EpiYear"]),
                        "epi_week": float(row["EpiWeek"]),
                        "week_start": row["Week_start"],
                        "g2r_label": row["g2r_label"],
                    }
                )
         
            # Update SQL DB with the log entry
            cursor.execute(
                        INSERT_LOG_QUERY,
                        get_log_entry(
                            row,  # old_data (the row being deleted)
                            None,  # new_data
                           "Mpox Trends - Delete"
                        ),
                    )
            log_entries.append(
                        get_log_entry(
                            row,  # old_data (the row being deleted)
                            None,  # new_data
                           "Mpox Trends - Delete"
                        )
                    )
                 
        # Remove from local DataFrame
        st.session_state.df_mpox.drop(index=selected_indices, inplace=True)
        st.session_state.df_mpox.reset_index(drop=True, inplace=True)

        # Log the new entry
        trigger_job_run("mpox", log_entries)

        # Show success message
        st.session_state.show_success_toast = True
        print("dialog triggered re-render")
        st.rerun()           


def app():
    if "show_success_toast" in st.session_state and st.session_state.show_success_toast:
        st.toast('Data successfully updated!', icon='✅')
        st.session_state.show_success_toast = False
        
    if "df_mpox" not in st.session_state:
        with st.spinner(
            "If the data cluster is cold starting, this may take up to 5 minutes",
            show_time=True,
        ):
            with get_cursor() as cursor:
                cursor.execute(FETCH_MPOX_QUERY)
                rows = [row.asDict() for row in cursor.fetchall()]
                st.session_state.df_mpox = pd.DataFrame(rows)

    # Create a dataframe where only a single-row is selectable
    selected_rows = st.dataframe(
        st.session_state.df_mpox,
        use_container_width=True,
        selection_mode="multi-row" if USER_CAN_EDIT else None,
        on_select="rerun" if USER_CAN_EDIT else "ignore",
        hide_index=True,
        column_config={
            "EpiYear": st.column_config.TextColumn(),
        },
    )

    # Get the index of the selected row, iff a row is selected
    if USER_CAN_EDIT and selected_rows.selection.get("rows", []):
        if st.button("Edit Selected Row(s)", type="primary"):
            edit_data_form(selected_rows.selection.rows)      
        if st.button("Delete Selected Row(s)", type="primary"):
            confirm_delete(selected_rows.selection.rows)

    if USER_CAN_EDIT:
        if st.button("{}\u2795 Add New Row".format(""), type="secondary"):
         add_new_row_form()


st.set_page_config(
    page_title="Mpox Trends",
    page_icon="🦠",
    layout="wide",
    initial_sidebar_state="expanded",
)

# hack to make the dialog box wider
st.markdown(
    """
    <style>
        div[data-testid="stDialog"] div[role="dialog"] {
            width: 80%;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🦠 Mpox Trends")
print("app re-render")
app()
st.markdown(
    """
## How to Use This App

1. Use the selection box on the left of any row to select the site(s) you want to modify
2. The selected row(s) will be highlighted to show they are active
3. Click on the "Edit Selected Row(s)/Delete Selected Rows(s)" to proceed with editing or deleting
4. Click "Submit" to save your changes

For any questions or issues, please contact the system administrator.
"""
)
