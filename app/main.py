"""
Main entry point for the Excel Duplicate Delete application.

This module serves as the central router for the application, handling:
- Global CSS styling application
- Session state initialization
- Page routing between home and workspace
- Main application execution flow

The main function orchestrates the entire application lifecycle,
ensuring proper initialization and routing between different views.
"""

import streamlit as st
from pathlib import Path
import sys

# Add the parent directory to sys.path to import from utils and constants
sys.path.append(str(Path(__file__).parent))

from config import AppConfig, initialize_session_state
from constants import CSS_STYLES
from pages import AVAILABLE_PAGES


def main():
    """
    Main function to run the Excel Duplicate Delete application.
    
    This function:
    1. Sets up page configuration
    2. Applies global CSS styling
    3. Initializes session state
    4. Routes to the appropriate page based on current state
    """
    
    # Set up page configuration
    st.set_page_config(
        page_title=AppConfig.APP_TITLE,
        layout=AppConfig.APP_LAYOUT,
        initial_sidebar_state=AppConfig.SIDEBAR_STATE
    )
    
    # Apply CSS styles
    st.markdown(CSS_STYLES, unsafe_allow_html=True)
    
    # Initialize session state
    initialize_session_state()
    
    # Route to the appropriate page based on session state
    current_page = st.session_state.get('current_page', 'home')
    
    if current_page in AVAILABLE_PAGES:
        page_function = AVAILABLE_PAGES[current_page]
        page_function()
    else:
        # Default to home page if invalid page state
        st.session_state.current_page = 'home'
        AVAILABLE_PAGES['home']()


if __name__ == "__main__":
    main()