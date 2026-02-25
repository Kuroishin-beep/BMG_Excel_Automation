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
import re
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
    
    # Custom CSS for colorful clean design
    st.markdown("""
        <style>
        /* Main color scheme */
        .orange-section { background: linear-gradient(135deg, #fff7ed 0%, #ffedd5 100%); }
        .blue-section { background: linear-gradient(135deg, #eff6ff 0%, #dbeafe 100%); }
        .green-section { background: linear-gradient(135deg, #f0fdf4 0%, #dcfce7 100%); }
        
        /* Navigation Bar */
        .nav-bar {
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            padding: 1.5rem 2rem;
            border-radius: 16px;
            margin-bottom: 2rem;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        }
        .nav-title {
            color: white !important;
            font-size: 1.8rem;
            font-weight: 700;
            margin: 0;
        }
        .nav-subtitle {
            color: white !important;
            font-size: 1rem;
            margin: 0.25rem 0 0 0;
        }
        .logo-container {
            display: flex;
            align-items: center;
            gap: 1rem;
        }
        .logo-image {
            height: 50px;
            width: auto;
        }
        
        /* Section Headers */
        .section-header-orange {
            background: linear-gradient(135deg, #f97316 0%, #fb923c 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(249, 115, 22, 0.3);
        }
        .section-header-blue {
            background: linear-gradient(135deg, #0284c7 0%, #38bdf8 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(2, 132, 199, 0.3);
        }
        .section-header-green {
            background: linear-gradient(135deg, #16a34a 0%, #4ade80 100%);
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 12px;
            font-size: 1.3rem;
            font-weight: 700;
            text-align: center;
            margin-bottom: 1.5rem;
            box-shadow: 0 4px 6px -1px rgba(22, 163, 74, 0.3);
        }
        
        /* Info boxes */
        .info-box-orange {
            background: #fff7ed;
            border-left: 5px solid #f97316;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            color: #7c2d12;
            font-size: 1rem;
        }
        .info-box-blue {
            background: #eff6ff;
            border-left: 5px solid #0284c7;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            color: #1e3a8a;
            font-size: 1rem;
        }
        .info-box-green {
            background: #f0fdf4;
            border-left: 5px solid #16a34a;
            padding: 1rem;
            border-radius: 8px;
            margin: 1rem 0;
            color: #14532d;
            font-size: 1rem;
        }
        
        /* Suggestion container */
        .suggestion-container {
            background: #fef3c7;
            border: 2px solid #fbbf24;
            border-radius: 12px;
            padding: 1rem;
            margin: 1rem 0;
        }
        .suggestion-label {
            color: #78350f;
            font-weight: 600;
            font-size: 0.95rem;
            margin-bottom: 0.5rem;
        }
        
        /* Stats box */
        .stats-box {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 1.25rem;
            margin: 1rem 0;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .stat-row {
            display: flex;
            justify-content: space-between;
            padding: 0.75rem 0;
            border-bottom: 1px solid #f3f4f6;
            font-size: 1.05rem;
        }
        .stat-row:last-child {
            border-bottom: none;
        }
        .stat-label {
            color: #6b7280;
            font-weight: 600;
        }
        .stat-value {
            color: #1f2937;
            font-weight: 700;
        }
        
        /* Legend */
        .legend-container {
            background: white;
            border: 2px solid #e5e7eb;
            border-radius: 12px;
            padding: 1rem;
            margin-top: 1rem;
        }
        .legend-title {
            font-weight: 700;
            color: #374151;
            margin-bottom: 0.5rem;
            font-size: 1rem;
        }
        .legend-item {
            display: inline-block;
            padding: 4px 12px;
            border-radius: 6px;
            margin: 0 8px 8px 0;
            font-size: 0.95rem;
            font-weight: 500;
        }
        
        /* Streamlit element overrides */
        .stTextInput > div > div > input {
            border-radius: 10px;
            border: 2px solid #f97316;
            font-size: 1.05rem;
            padding: 0.75rem;
        }
        .stTextInput > div > div > input:focus {
            border-color: #fb923c;
            box-shadow: 0 0 0 3px rgba(249, 115, 22, 0.1);
        }
        
        /* Button styling */
        .stButton > button {
            border-radius: 10px;
            font-weight: 600;
            font-size: 1rem;
            padding: 0.75rem 1.5rem;
            transition: all 0.2s;
        }
        .stButton > button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.15);
        }
        
        /* Download button special styling */
        .stDownloadButton > button {
            background: linear-gradient(135deg, #16a34a 0%, #22c55e 100%);
            color: white;
            border: none;
            font-size: 1.1rem;
            font-weight: 700;
            padding: 1rem;
        }
        
        /* Dataframe styling */
        .dataframe {
            border-radius: 12px;
            overflow: hidden;
            border: 2px solid #e5e7eb;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Load logo
    logo_url = load_logo()
    
    # Navigation Bar with Back Link and Logo
    if logo_url:
        st.markdown(f"""
            <div class="nav-bar">
                <div class="logo-container">
                    <img src="{logo_url}" class="logo-image" alt="Logo">
                    <div>
                        <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                        <p class="nav-subtitle">{UI_LABELS['WORKSPACE_SUBTITLE']}</p>
                    </div>
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="nav-bar">
                <h2 class="nav-title">{AppConfig.APP_TITLE}</h2>
                <p class="nav-subtitle">{UI_LABELS['WORKSPACE_SUBTITLE']}</p>
            </div>
        """, unsafe_allow_html=True)
    
    # Navigation button for segregation
    col_segregate, col_space = st.columns([1.5, 5.5])
    with col_segregate:
        if st.button("📚 Book Segregation", use_container_width=True, key="direct_segregation_btn", type="secondary"):
            go_to_segregation()
    
    # Verify we have data
    if st.session_state.df_original is None:
        st.error("No file loaded. Please return to home and upload a file.")
        st.stop()
    
    # Create three-column layout for the main interface
    column_left, column_center, column_right = st.columns([3, 2, 3])

    # =============================================================================================
    # LEFT COLUMN: SEARCH AND ADD TO QUEUE (ORANGE)
    # =============================================================================================
    
    with column_left:
        st.markdown('<div class="section-header-orange">Step 1: Search for Duplicates</div>', unsafe_allow_html=True)
        
        # Generate search suggestions from Excel data
        if 'search_suggestions' not in st.session_state or st.session_state.search_suggestions is None:
            all_values = set()
            for col in st.session_state.df_original.columns:
                try:
                    unique_vals = st.session_state.df_original[col].dropna().astype(str).unique()
                    all_values.update([v for v in unique_vals if len(v) > 0][:100])
                except:
                    continue
            st.session_state.search_suggestions = sorted(list(all_values))
        
        # Search input field
        search_text = st.text_input(
            "Type to search your data", 
            help="Search is case-sensitive",
            key="search_input_workspace"
        )
        
        # --- SEARCH LOGIC ---
        if search_text:
            df = st.session_state.df_original
            
            # 1. Base Search: Find rows explicitly containing the text
            found_indices = get_rows_to_delete_logic(df, search_text)
            
            # Helper function to find column names case-insensitively
            def get_col_name(candidates):
                cols_map = {c.lower().strip(): c for c in df.columns}
                for cand in candidates:
                    if cand in cols_map:
                        return cols_map[cand]
                return None

            # 2. Journal ID Logic: Find siblings via ID
            id_col = get_col_name(["journal id", "journal no", "id", "transaction id", "ref no", "reference"])
            
            if id_col and found_indices:
                matched_ids = df.loc[found_indices, id_col].unique()
                # Filter out empty/NaN IDs
                valid_ids = [x for x in matched_ids if pd.notna(x) and str(x).strip() != ""]
                
                if valid_ids:
                    related_by_id = df[df[id_col].isin(valid_ids)].index.tolist()
                    found_indices = list(set(found_indices + related_by_id))

            # 3. Narration Logic: Find siblings via Description/Narration
            narr_col = get_col_name(["narration", "description", "particulars", "memo", "notes"])
            
            if narr_col and found_indices:
                # Get the narration text from the rows we have found so far
                matched_narrations = df.loc[found_indices, narr_col].unique()
                # Filter out empty/NaN narrations to avoid selecting all blank rows
                valid_narrations = [x for x in matched_narrations if pd.notna(x) and str(x).strip() != ""]
                
                if valid_narrations:
                    # Find ALL rows that have these specific narrations
                    related_by_narr = df[df[narr_col].isin(valid_narrations)].index.tolist()
                    found_indices = list(set(found_indices + related_by_narr))
            
            st.session_state.current_matches = found_indices
        else:
            st.session_state.current_matches = []
        # ------------------------------------------------------

        # Display match count and add button
        match_count = len(st.session_state.current_matches)
        
        if match_count > 0:
            st.markdown(f'<div class="info-box-orange">✓ Found {match_count} related rows</div>', unsafe_allow_html=True)
            
            add_button_label = f"Add {match_count} row{'s' if match_count != 1 else ''} to deletion queue"
            if st.button(add_button_label, use_container_width=True, type="primary"):
                st.session_state.deletion_queue.update(st.session_state.current_matches)
                st.session_state.current_matches = []
                st.rerun()
        elif search_text:
            st.markdown('<div class="info-box-orange">No matching rows found. Try a different search term.</div>', unsafe_allow_html=True)

        # Display dataframe with color-coded highlighting
        st.write("")
        st.markdown("**Your Excel Data:**")
        
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
            <div class="legend-container">
                <div class="legend-title">Color Guide:</div>
                <span class="legend-item" style='background: {COLOR_CODES["RED_HIGHLIGHT"]};'>Will be deleted</span>
                <span class="legend-item" style='background: {COLOR_CODES["YELLOW_HIGHLIGHT"]};'>Transaction group found</span>
            </div>
        """, unsafe_allow_html=True)

    # =============================================================================================
    # CENTER COLUMN: REVIEW AND MANAGE QUEUE (BLUE)
    # =============================================================================================
    
    with column_center:
        st.markdown('<div class="section-header-blue">Step 2: Review Queue</div>', unsafe_allow_html=True)
        
        # Get sorted list of queued rows
        queue_list = sorted(list(st.session_state.deletion_queue))
        
        if queue_list:
            st.markdown(f'<div class="info-box-blue">{len(queue_list)} row{"s" if len(queue_list) != 1 else ""} marked for deletion</div>', unsafe_allow_html=True)
            
            # Display the rows currently in the deletion queue
            delete_dataframe = st.session_state.df_original.iloc[queue_list].copy()
            delete_dataframe.insert(0, "Row #", [pandas_idx + 2 for pandas_idx in queue_list])
            
            st.markdown("**Rows to be deleted:**")
            st.dataframe(delete_dataframe, height=AppConfig.PREVIEW_HEIGHT, use_container_width=True)

            # Disregard all button
            st.write("")
            if st.button("Clear All from Queue", use_container_width=True, type="secondary"):
                st.session_state.deletion_queue = set()
                st.rerun()

        else:
            st.markdown('<div class="info-box-blue">Your deletion queue is empty. Search and add rows to delete them.</div>', unsafe_allow_html=True)

    # =============================================================================================
    # RIGHT COLUMN: PREVIEW AND DOWNLOAD (GREEN)
    # =============================================================================================

    with column_right:
        st.markdown('<div class="section-header-green">Step 3: Preview & Download</div>', unsafe_allow_html=True)
        
        # Get current queue list
        queue_list = sorted(list(st.session_state.deletion_queue))
        
        # Create the specific view you see on screen
        df_to_show = st.session_state.df_original.drop(queue_list, errors='ignore')
        
        st.markdown("**Final Result Preview:**")
        st.dataframe(df_to_show, height=AppConfig.DATAFRAME_HEIGHT, use_container_width=True)
        
        # Display statistics
        stats = get_queue_statistics(st.session_state.df_original, st.session_state.deletion_queue)
        
        st.markdown(f"""
            <div class="stats-box">
                <div class="stat-row">
                    <span class="stat-label">Original Rows:</span>
                    <span class="stat-value">{stats['original_rows']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Rows to Delete:</span>
                    <span class="stat-value" style="color: #dc2626;">{stats['rows_to_delete']}</span>
                </div>
                <div class="stat-row">
                    <span class="stat-label">Final Rows:</span>
                    <span class="stat-value" style="color: #16a34a;">{stats['final_rows']}</span>
                </div>
            </div>
        """, unsafe_allow_html=True)
        
        st.write("---")
        
        # Download button
        if queue_list:
            from io import BytesIO
            
            # Generate filename
            original = st.session_state.get("original_filename", "Excel_File.xlsx")
            base = re.sub(r"\.xlsx?$", "", original, flags=re.IGNORECASE)
            output_name = f"{base}_Cleaned.xlsx"

            # ------------------------------------------------------------------
            # Download EXACTLY what is in the preview 
            # ------------------------------------------------------------------
            buffer = BytesIO()
            with st.spinner("Generating  Excel file..."):
                # pandas to write the dataframe directly to a new file.
                # index=False ensures we don't add an extra number column on the left.
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    df_to_show.to_excel(writer, index=False)
                
                # Get the data
                processed_excel_data = buffer.getvalue()
                
                # Update session state for the next page
                st.session_state.processed_file_data = processed_excel_data
                st.session_state.processed_df = df_to_show
            
            st.download_button(
                label="Download Cleaned Excel File",
                data=processed_excel_data,
                file_name=output_name,
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True,
                type="primary",
                on_click=lambda: st.session_state.update({'show_modal': True}),
                icon="📥"
            )
        else:
            st.markdown('<div class="info-box-green">Add rows to the deletion queue to enable download.</div>', unsafe_allow_html=True)