"""
Settings page module for the Excel Duplicate Delete application.

This module allows users to configure application preferences
such as duplicate detection behavior and output options.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from utils import load_logo
from constants import CSS_STYLES, UI_LABELS
from config import AppConfig, initialize_session_state


def render_settings_page():
    """
    Render the settings page.
    """

    # Initialize session state
    initialize_session_state()

    # Apply global CSS
    st.markdown(CSS_STYLES, unsafe_allow_html=True)

    # Load logo
    logo_url = load_logo()

    # =========================
    # APP BAR (Same as Home)
    # =========================
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
                </div>
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="app-bar">
                <div class="app-bar-content">
                    <h1>{AppConfig.APP_TITLE}</h1>
                    <p>{UI_LABELS['APP_DESCRIPTION']}</p>
                </div>
            </div>
        """, unsafe_allow_html=True)

    # =========================
    # SETTINGS HEADER CARD
    # =========================
    st.markdown("""
        <div class="upload-container">
            <div class="upload-card">
                <h2 class="upload-header">Application Settings</h2>
                <p class="upload-subheader">
                    Customize how duplicate detection and file processing works.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # =========================
    # SETTINGS FORM
    # =========================
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("settings_form"):

            st.subheader("Duplicate Detection")

            ignore_case = st.checkbox(
                "Ignore case when comparing values",
                value=st.session_state.get("ignore_case", True)
            )

            trim_whitespace = st.checkbox(
                "Trim leading and trailing spaces",
                value=st.session_state.get("trim_whitespace", True)
            )

            keep_first = st.radio(
                "When duplicates are found, keep:",
                options=["First occurrence", "Last occurrence"],
                index=0 if st.session_state.get("keep_first", True) else 1
            )

            st.divider()

            st.subheader("Output Options")

            preserve_formatting = st.checkbox(
                "Preserve original Excel formatting",
                value=st.session_state.get("preserve_formatting", True)
            )

            add_summary_sheet = st.checkbox(
                "Add summary sheet after processing",
                value=st.session_state.get("add_summary_sheet", False)
            )

            st.divider()

            st.subheader("General")

            auto_proceed = st.checkbox(
                "Automatically proceed after file upload",
                value=st.session_state.get("auto_proceed", False)
            )

            submitted = st.form_submit_button(
                "Save Settings",
                use_container_width=True,
                type="primary"
            )

        if submitted:
            # Save to session state
            st.session_state.ignore_case = ignore_case
            st.session_state.trim_whitespace = trim_whitespace
            st.session_state.keep_first = (keep_first == "First occurrence")
            st.session_state.preserve_formatting = preserve_formatting
            st.session_state.add_summary_sheet = add_summary_sheet
            st.session_state.auto_proceed = auto_proceed

            st.success("Settings saved successfully ✅")

    # =========================
    # SETTINGS INFO
    # =========================
    st.markdown("""
        <div class="upload-container">
            <div class="upload-card">
                <div class="upload-instructions">
                    <h3>Tips</h3>
                    <ul class="instruction-list">
                        <li>
                            <span class="instruction-step">Accuracy:</span>
                            Enable trimming and case-insensitive comparison for best results
                        </li>
                        <li>
                            <span class="instruction-step">Safety:</span>
                            Keeping the first occurrence is usually recommended
                        </li>
                        <li>
                            <span class="instruction-step">Reporting:</span>
                            Summary sheets help track removed duplicates
                        </li>
                    </ul>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
