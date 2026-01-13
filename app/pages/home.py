"""
Home page module for the Excel Duplicate Delete application.

This module contains the implementation of the home page which serves as
the entry point for the application. It includes:
- File upload functionality
- Logo display and branding
- Instructions and usage guide
- Navigation to the workspace page
- Responsive design elements

The home page is responsible for initializing the session state and
handling the file upload process before directing users to the workspace.
"""

import streamlit as st
import pandas as pd
from pathlib import Path
import sys
from pathlib import Path

# Add the parent directory to sys.path to import from utils and constants
sys.path.append(str(Path(__file__).parent.parent))

from utils import load_logo, process_excel_with_formatting
from constants import CSS_STYLES, UI_LABELS, HELP_TEXTS
from config import AppConfig, initialize_session_state


def render_home_page():
    """
    Render the home page with file upload and instructions.
    
    This function creates the complete home page interface including:
    - Application header with logo
    - Centered file upload section
    - How-to-use instructions
    - Footer with branding
    """
    
    # Load logo
    logo_url = load_logo()
    
    # Application Bar with Logo and Navigation
    if logo_url:
        st.markdown(f"""
            <div class="app-bar">
                <div class="app-bar-content">
                    <div class="logo-container">
                        <img src="{logo_url}" class="logo-image" alt="Logo">
                        <div class="logo-text">
                            <h1>{AppConfig.APP_TITLE}</h1>
                            <p>{UI_LABELS['APP_DESCRIPTION']}</p>
                        </div>
                    </div>
                    <div class="nav-buttons">
                        <button class="nav-button" onclick="setPage('settings')">⚙️ Settings</button>
                        <button class="nav-button" onclick="setPage('feedback')">💬 Feedback</button>
                    </div>
                </div>
            </div>
            <script>
                function setPage(page) {{
                    const event = new CustomEvent('streamlit:setPage', {{ detail: {{ page: page }} }});
                    window.dispatchEvent(event);
                }}
            </script>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="app-bar">
                <div class="app-bar-content">
                    <div style="display: flex; justify-content: space-between; align-items: center; width: 100%;">
                        <div>
                            <h1>{AppConfig.APP_TITLE}</h1>
                            <p>{UI_LABELS['APP_DESCRIPTION']}</p>
                        </div>
                        <div class="nav-buttons">
                            <button class="nav-button" onclick="setPage('settings')">⚙️ Settings</button>
                            <button class="nav-button" onclick="setPage('feedback')">💬 Feedback</button>
                        </div>
                    </div>
                </div>
            </div>
            <script>
                function setPage(page) {{
                    const event = new CustomEvent('streamlit:setPage', {{ detail: {{ page: page }} }});
                    window.dispatchEvent(event);
                }}
            </script>
        """, unsafe_allow_html=True)
    
    # Alternative approach using Streamlit buttons if JavaScript doesn't work well
    # Add this after the app bar if needed:
    # nav_col1, nav_col2 = st.columns([1, 1])
    # with nav_col1:
    #     if st.button("⚙️ Settings", use_container_width=True):
    #         st.session_state.current_page = 'settings'
    #         st.rerun()
    # with nav_col2:
    #     if st.button("💬 Feedback", use_container_width=True):
    #         st.session_state.current_page = 'feedback'
    #         st.rerun()

    # CSS for navigation buttons
    st.markdown("""
        <style>
        .nav-buttons {
            display: flex;
            gap: 10px;
            align-items: center;
        }
        
        .nav-button {
            background-color: #f0f2f6;
            border: 1px solid #d3d3d3;
            border-radius: 4px;
            padding: 8px 12px;
            cursor: pointer;
            font-size: 14px;
            transition: all 0.3s ease;
        }
        
        .nav-button:hover {
            background-color: #e0e0e0;
            transform: translateY(-1px);
        }
        
        .app-bar-content {
            display: flex;
            justify-content: space-between;
            align-items: center;
        }
        </style>
    """, unsafe_allow_html=True)
    
    # Centered Upload Section
    st.markdown(f"""
        <div class="upload-container">
            <div class="upload-card">
                <h2 class="upload-header">{UI_LABELS['UPLOAD_HEADER']}</h2>
                <p class="upload-subheader">{UI_LABELS['UPLOAD_SUBHEADER']}</p>
            </div>
        </div>
    """, unsafe_allow_html=True)
    
    # File Uploader (Centered)
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        uploaded_file = st.file_uploader(
            "Upload an Excel file", 
            type=AppConfig.SUPPORTED_FILE_TYPES,
            help=HELP_TEXTS['FILE_UPLOADER'],
            key="file_uploader_home"
        )
        
        if uploaded_file is not None:
            # Store file in session state
            st.session_state.uploaded_file = uploaded_file
            st.session_state.original_filename = uploaded_file.name
            
            # Show spinner while loading
            with st.spinner("Loading your Excel file..."):
                raw_df = pd.read_excel(
                    uploaded_file,
                    engine="openpyxl",
                    header=None
                )

                #Use row index 3 as the header
                raw_df.columns = raw_df.iloc[4]

                #Drop rows above the header and the header row itself
                df = raw_df.iloc[4:].reset_index(drop=True)

                #Drop completely empty columns 
                df = df.dropna(axis=1, how="all")

                st.session_state.df_original = df.copy()

                # Streamlit debug
                st.write("Detected headers:")
                st.code(list(df.columns))

                
            # Show success and proceed button
            st.success(f"File uploaded successfully! Found {len(df)} rows.")
            
            if st.button(UI_LABELS['PROCEED_BUTTON'], use_container_width=True, type="primary"):
                st.session_state.current_page = 'workspace'
                st.rerun()
    
    # Instructions
    st.markdown(f"""
        <div class="upload-container">
            <div class="upload-card">
                <div class="upload-instructions">
                    <h3>{UI_LABELS['HOW_IT_WORKS_TITLE']}</h3>
                    <ol class="instruction-list">
                        <li>
                            <span class="instruction-step">{UI_LABELS['INSTRUCTION_STEP_1']}:</span> 
                            {UI_LABELS['INSTRUCTION_DESC_1']}
                        </li>
                        <li>
                            <span class="instruction-step">{UI_LABELS['INSTRUCTION_STEP_2']}:</span> 
                            {UI_LABELS['INSTRUCTION_DESC_2']}
                        </li>
                        <li>
                            <span class="instruction-step">{UI_LABELS['INSTRUCTION_STEP_3']}:</span> 
                            {UI_LABELS['INSTRUCTION_DESC_3']}
                        </li>
                        <li>
                            <span class="instruction-step">{UI_LABELS['INSTRUCTION_STEP_4']}:</span> 
                            {UI_LABELS['INSTRUCTION_DESC_4']}
                        </li>
                        <li>
                            <span class="instruction-step">{UI_LABELS['INSTRUCTION_STEP_5']}:</span> 
                            {UI_LABELS['INSTRUCTION_DESC_5']}
                        </li>
                    </ol>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)

