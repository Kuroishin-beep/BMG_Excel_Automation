"""
Workspace page module for the Excel Duplicate Delete application.

This module contains the implementation of the main processing page where
users interact with their uploaded Excel data. It includes:
- Search functionality with auto-suggestions based on Excel data
- Deletion queue management system
- Real-time preview of changes
- Data visualization with color-coded highlighting
- File download functionality with preserved formatting
- Post-download modal for segregation option
- Seamless data transfer to segregation module
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from pathlib import Path

# Add the parent directory to sys.path to import from utils and constants
sys.path.append(str(Path(__file__).parent.parent))

from utils import load_logo, process_excel_with_formatting, apply_row_highlighting, get_rows_to_delete_logic, get_queue_statistics
from constants import CSS_STYLES, UI_LABELS, COLOR_CODES
from config import AppConfig


def go_to_home():
    """Navigate back to home page and reset state."""
    st.session_state.current_page = 'home'
    st.session_state.df_original = None
    st.session_state.deletion_queue = set()
    st.session_state.current_matches = []
    st.session_state.uploaded_file = None
    st.session_state.original_filename = None
    st.session_state.search_suggestions = None
    st.session_state.selected_suggestion = ""
    # Clear processed data
    if 'processed_df' in st.session_state:
        del st.session_state.processed_df
    if 'processed_file_data' in st.session_state:
        del st.session_state.processed_file_data


def go_to_segregation():
    """Navigate to segregation page with processed data."""
    # Ensure we have the latest processed dataframe ready for segregation
    queue_list = sorted(list(st.session_state.deletion_queue))
    
    if queue_list:
        # Create the cleaned dataframe
        st.session_state.processed_df = st.session_state.df_original.drop(queue_list, errors='ignore')
    else:
        # If no deletions, use the original data
        st.session_state.processed_df = st.session_state.df_original.copy()
    
    # Navigate to segregation page
    st.session_state.current_page = 'segregation'
    st.rerun()


@st.dialog("Download Complete")
def show_segregation_modal():
    """Show modal after successful download with segregation option."""
    st.markdown("""
        <style>
        .modal-content {
            text-align: center;
            padding: 1rem;
        }
        .modal-title {
            font-size: 1.5rem;
            font-weight: 700;
            color: #1e293b;
            margin-bottom: 1rem;
        }
        .modal-description {
            font-size: 1rem;
            color: #475569;
            margin-bottom: 1.5rem;
            line-height: 1.6;
        }
        </style>
    """, unsafe_allow_html=True)
    
    st.markdown("""
        <div class="modal-content">
            <div class="modal-title">File Downloaded Successfully</div>
            <div class="modal-description">
                Your Excel file has been processed and downloaded.<br>
                Would you like to segregate the cleaned data into multiple books?
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Segregate Data", use_container_width=True, type="primary"):
            st.session_state.show_modal = False
            go_to_segregation()
    
    with col2:
        if st.button("Done", use_container_width=True):
            st.session_state.show_modal = False
            st.rerun()
    
    st.markdown("---")
    st.markdown("""
        <div style='background: #f0f9ff; padding: 0.75rem; border-radius: 8px; border-left: 4px solid #3b82f6;'>
            <p style='margin: 0; color: #1e40af; font-size: 0.9rem;'>
                <strong>What is Book Segregation?</strong><br>
                <span style='font-size: 0.85rem;'>
                Automatically classify and split your data into:<br>
                • Cash Disbursement (expenses, payments)<br>
                • Cash Receipts (income, collections)<br>
                • General Journal (other transactions)
                </span>
            </p>
        </div>
    """, unsafe_allow_html=True)


def render_workspace_page():
    """
    Render the workspace page with 3-column layout for data processing.
    
    This function creates the main processing interface with three distinct
    columns: search and queue management (left), queue review (center),
    and preview/download (right). Each column handles specific aspects
    of the duplicate removal workflow.
    """
    
    # Initialize modal state if not exists
    if 'show_modal' not in st.session_state:
        st.session_state.show_modal = False
    
    # Initialize selected suggestion state
    if 'selected_suggestion' not in st.session_state:
        st.session_state.selected_suggestion = ""
    
    # Show modal if triggered
    if st.session_state.show_modal:
        show_segregation_modal()
    
    # Load logo
    logo_url = load_logo()
    
    # Navigation Bar with Back Link and Logo
    if logo_url:
        st.markdown(f"""
            <div class="nav-bar">
                <div class="nav-left">
                    <div class="logo-container">
                        <img src="{logo_url}" class="logo-image" alt="Logo">
                        <div class="logo-text">
                            <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                            <p class="nav-subtitle">{UI_LABELS['WORKSPACE_SUBTITLE']}</p>
                        </div>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="nav-bar">
                <div class="nav-left">
                    <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                    <p class="nav-subtitle">{UI_LABELS['WORKSPACE_SUBTITLE']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)
    
    # Navigation button for segregation
    col_segregate, col_space = st.columns([1.5, 5.5])
    with col_segregate:
        st.markdown("""
            <style>
            .segregate-link-container {
                margin-top: -3rem;
                margin-bottom: 2rem;
            }
            </style>
            <div class="segregate-link-container">
        """, unsafe_allow_html=True)
        
        if st.button("Book Segregation", use_container_width=True, key="direct_segregation_btn", type="secondary"):
            go_to_segregation()
        
        st.markdown("</div>", unsafe_allow_html=True)
    
    st.markdown('<div class="content-wrapper">', unsafe_allow_html=True)
    
    # Verify we have data
    if st.session_state.df_original is None:
        st.error("No file loaded. Please return to home and upload a file.")
        st.stop()
    
    # Create three-column layout for the main interface
    column_left, column_center, column_right = st.columns([3, 2, 3])

    # =============================================================================================
    # LEFT COLUMN: SEARCH AND ADD TO QUEUE
    # =============================================================================================
    
    with column_left:
        st.markdown(f'<h3 class="section-header">{UI_LABELS["STEP_1_HEADER"]}</h3>', unsafe_allow_html=True)
        
        # Generate search suggestions from Excel data (cached in session state)
        if 'search_suggestions' not in st.session_state or st.session_state.search_suggestions is None:
            # Get all unique non-null values from the dataframe
            all_values = set()
            for col in st.session_state.df_original.columns:
                try:
                    unique_vals = st.session_state.df_original[col].dropna().astype(str).unique()
                    # Limit to 100 values per column for performance
                    all_values.update([v for v in unique_vals if len(v) > 0][:100])
                except:
                    continue
            st.session_state.search_suggestions = sorted(list(all_values))
        
        # Search input field
        search_text = st.text_input(
            "Search text (Case Sensitive)", 
            value=st.session_state.selected_suggestion,
            placeholder="Type to search and see suggestions...",
            help="Search is case-sensitive. Start typing to see suggestions from your data.",
            key="search_input_workspace"
        )
        
        # Display matching suggestions as user types
        if search_text and len(search_text) >= 2:
            matching_suggestions = [
                s for s in st.session_state.search_suggestions 
                if search_text.lower() in s.lower()
            ][:10]
            
            if matching_suggestions:
                st.markdown("""
                    <style>
                    .suggestion-container {
                        margin: 0.5rem 0 1rem 0;
                        padding: 0.75rem;
                        background: #f8fafc;
                        border-radius: 8px;
                        border: 1px solid #e2e8f0;
                    }
                    .suggestion-label {
                        font-size: 0.85rem;
                        font-weight: 600;
                        color: #475569;
                        margin-bottom: 0.5rem;
                    }
                    </style>
                    <div class="suggestion-container">
                        <div class="suggestion-label">Suggestions from your data:</div>
                    </div>
                """, unsafe_allow_html=True)
                
                # Display suggestions in columns
                num_cols = min(1, len(matching_suggestions))
                suggestion_cols = st.columns(num_cols)
                
                for idx, suggestion in enumerate(matching_suggestions):
                    col_idx = idx % num_cols
                    with suggestion_cols[col_idx]:
                        display_text = suggestion if len(suggestion) <= 25 else f"{suggestion[:22]}..."
                        if st.button(
                            display_text, 
                            key=f"suggest_{idx}_{suggestion[:10]}", 
                            use_container_width=True,
                            help=f"Click to search: {suggestion}"
                        ):
                            st.session_state.selected_suggestion = suggestion
                            st.rerun()

        # Execute search logic
        if search_text:
            found_indices = get_rows_to_delete_logic(st.session_state.df_original, search_text)
            st.session_state.current_matches = found_indices
        else:
            st.session_state.current_matches = []

        # Display match count and add button
        match_count = len(st.session_state.current_matches)
        
        if match_count > 0:
            st.success(f"Found {match_count} matching row(s) in your Excel file.")
            
            add_button_label = UI_LABELS['ADD_TO_QUEUE_BUTTON'].format(count=match_count)
            if st.button(add_button_label, use_container_width=True):
                st.session_state.deletion_queue.update(st.session_state.current_matches)
                st.session_state.current_matches = []
                st.session_state.selected_suggestion = ""
                st.rerun()
        elif search_text:
            st.info("No matching rows found. Try a different search term.")

        # Display dataframe with color-coded highlighting
        st.write("")
        st.write(f"**{UI_LABELS['ORIGINAL_DATA_PREVIEW']}**:")
        
        df_display = st.session_state.df_original.copy()

        def apply_row_highlighting_wrapper(row):
            """Wrapper to apply row highlighting with current session state values."""
            return apply_row_highlighting(
                row, 
                st.session_state.deletion_queue, 
                st.session_state.current_matches
            )

        try:
            styled_dataframe = df_display.style.apply(apply_row_highlighting_wrapper, axis=1)
            st.dataframe(styled_dataframe, height=AppConfig.DATAFRAME_HEIGHT, use_container_width=True)
        except Exception as e:
            st.dataframe(df_display, height=AppConfig.DATAFRAME_HEIGHT, use_container_width=True)
        
        # Legend for color coding
        st.markdown(f"""
            <div style='font-size: 0.9rem; color: #64748b; margin-top: 1rem;'>
                <strong>Legend:</strong> 
                <span style='background: {COLOR_CODES["RED_HIGHLIGHT"]}; padding: 2px 8px; border-radius: 4px; margin: 0 5px;'>{UI_LABELS["LEGEND_RED"]}</span>
                <span style='background: {COLOR_CODES["YELLOW_HIGHLIGHT"]}; padding: 2px 8px; border-radius: 4px;'>{UI_LABELS["LEGEND_YELLOW"]}</span>
            </div>
        """, unsafe_allow_html=True)

    # =============================================================================================
    # CENTER COLUMN: REVIEW AND MANAGE QUEUE
    # =============================================================================================
    
    with column_center:
        st.markdown(f'<h3 class="section-header">{UI_LABELS["STEP_2_HEADER"]}</h3>', unsafe_allow_html=True)
        
        # Get sorted list of queued rows
        queue_list = sorted(list(st.session_state.deletion_queue))
        
        if queue_list:
            queue_status_text = UI_LABELS['QUEUE_STATUS'].format(count=len(queue_list))
            st.warning(queue_status_text)
            
            # Display the rows currently in the deletion queue
            delete_dataframe = st.session_state.df_original.iloc[queue_list].copy()
            delete_dataframe.insert(0, "Excel Row", [pandas_idx + 2 for pandas_idx in queue_list])
            
            st.write(f"**{UI_LABELS['ROWS_MARKED_FOR_DELETION']}**")
            st.dataframe(delete_dataframe, height=AppConfig.PREVIEW_HEIGHT, use_container_width=True)

            # Disregard all button
            st.write("")
            if st.button("Disregard All", use_container_width=True, type="secondary"):
                st.session_state.deletion_queue = set()
                st.rerun()

        else:
            st.info(UI_LABELS['EMPTY_QUEUE_MESSAGE'])

    # =============================================================================================
    # RIGHT COLUMN: PREVIEW AND DOWNLOAD
    # =============================================================================================

    with column_right:
        st.markdown(f'<h3 class="section-header">{UI_LABELS["STEP_3_HEADER"]}</h3>', unsafe_allow_html=True)
        
        # Get current queue list
        queue_list = sorted(list(st.session_state.deletion_queue))
        
        # Always show preview (after deletion)
        df_to_show = st.session_state.df_original.drop(queue_list, errors='ignore')
        preview_title = UI_LABELS['FINAL_RESULT_PREVIEW']
        
        st.write(f"**{preview_title}**")
        st.dataframe(df_to_show, height=AppConfig.DATAFRAME_HEIGHT, use_container_width=True)
        
        # Display statistics
        stats = get_queue_statistics(st.session_state.df_original, st.session_state.deletion_queue)
        
        st.markdown(f"""
            <div style='background: #f8fafc; padding: 1rem; border-radius: 8px; margin: 1rem 0;'>
                <p style='margin: 0.25rem 0; color: #475569;'>
                    <strong>Original Rows:</strong> {stats['original_rows']}
                </p>
                <p style='margin: 0.25rem 0; color: #475569;'>
                    <strong>Rows to Delete:</strong> {stats['rows_to_delete']}
                </p>
                <p style='margin: 0.25rem 0; color: #475569;'>
                    <strong>Final Rows:</strong> {stats['final_rows']}
                </p>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Download button
        if queue_list:
            with st.spinner("Processing your Excel file..."):
                processed_excel_data = process_excel_with_formatting(
                    st.session_state.uploaded_file, 
                    queue_list
                )
                
                st.session_state.processed_file_data = processed_excel_data
                st.session_state.processed_df = st.session_state.df_original.drop(queue_list, errors='ignore')
            
            st.download_button(
                label=UI_LABELS['DOWNLOAD_BUTTON'],
                data=processed_excel_data,
                file_name=st.session_state.original_filename,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
                on_click=lambda: st.session_state.update({'show_modal': True})
            )
        else:
            st.info(UI_LABELS['NO_ROWS_MESSAGE'])
    
