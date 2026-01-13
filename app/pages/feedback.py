"""
Feedback page module for the Excel Duplicate Delete application.

This module allows users to submit feedback about the application,
including suggestions, issues, and overall experience.
"""

import streamlit as st
from pathlib import Path
import sys

# Add parent directory to sys.path
sys.path.append(str(Path(__file__).parent.parent))

from utils import load_logo
from constants import CSS_STYLES, UI_LABELS, HELP_TEXTS
from config import AppConfig, initialize_session_state


def render_feedback_page():
    """
    Render the feedback page.
    """

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
    # FEEDBACK CARD
    # =========================
    st.markdown("""
        <div class="upload-container">
            <div class="upload-card">
                <h2 class="upload-header">We’d Love Your Feedback</h2>
                <p class="upload-subheader">
                    Help us improve the Excel Duplicate Delete tool by sharing your experience.
                </p>
            </div>
        </div>
    """, unsafe_allow_html=True)

    # Centered Form
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        with st.form("feedback_form"):
            name = st.text_input("Your Name (optional)")
            email = st.text_input("Email (optional)")
            rating = st.select_slider(
                "Overall Experience",
                options=["Very Bad", "Bad", "Okay", "Good", "Excellent"]
            )
            feedback = st.text_area(
                "Your Feedback",
                placeholder="Share your suggestions, issues, or comments here...",
                height=150
            )

            submitted = st.form_submit_button("Submit Feedback", use_container_width=True)

        if submitted:
            # You can later save this to a DB / file / email
            st.success("Thank you for your feedback! 🙏")

    # =========================
    # OPTIONAL INFO SECTION
    # =========================
    st.markdown("""
        <div class="upload-container">
            <div class="upload-card">
                <div class="upload-instructions">
                    <h3>Why Your Feedback Matters</h3>
                    <ul class="instruction-list">
                        <li><span class="instruction-step">Improve:</span> Helps us enhance features</li>
                        <li><span class="instruction-step">Fix:</span> Identifies bugs and issues</li>
                        <li><span class="instruction-step">Enhance:</span> Shapes future updates</li>
                    </ul>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)
