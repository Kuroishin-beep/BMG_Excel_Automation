"""
Configuration module for the Excel Duplicate Delete application.

This module contains all configuration settings, constants, and paths used throughout
the application. It centralizes configuration management to make the application
more maintainable and easier to modify without touching core logic.

Contains:
- File paths and directory configurations
- Application settings and parameters
- Styling configurations
- Default values for various components
"""

import streamlit as st
from pathlib import Path

class AppConfig:
    """Centralized configuration class for the Excel Duplicate Delete application."""
    
    # Application metadata
    APP_TITLE = "Excel Duplicate Delete"
    APP_LAYOUT = "wide"
    SIDEBAR_STATE = "collapsed"
    
    # Logo configuration
    LOGO_PATH = Path(r"C:\Users\Aaron Carl\bmg-finance-automation\images\logo.png")
    
    # File upload settings
    SUPPORTED_FILE_TYPES = ["xlsx", "xls"]
    FILE_UPLOAD_HELP_TEXT = "Select your Excel file (.xlsx or .xls format)"
    
    # Styling configurations
    PRIMARY_COLOR = "#1e3c72"
    SECONDARY_COLOR = "#2a5298"
    SUCCESS_COLOR = "#059669"
    WARNING_COLOR = "#f59e0b"
    ERROR_COLOR = "#ef4444"
    
    # UI component settings
    UPLOAD_CARD_WIDTH = 800
    DATAFRAME_HEIGHT = 500
    PREVIEW_HEIGHT = 300
    
    # Page navigation settings
    PAGES = {
        'home': 'home',
        'workspace': 'workspace',
        'segregation': 'segregation'

    }
    
    # Session state keys
    SESSION_KEYS = [
        'current_page',
        'df_original', 
        'deletion_queue',
        'current_matches',
        'uploaded_file',
        'original_filename',
        'view_mode',
        'search_suggestions'
        'segregation'
    ]
    
    @staticmethod
    def get_default_session_state():
        """Return default session state configuration."""
        return {
            'current_page': 'home',
            'df_original': None,
            'deletion_queue': set(),
            'current_matches': [],
            'uploaded_file': None,
            'original_filename': None,
            'view_mode': 'original',
            'search_suggestions': None
        }

def initialize_session_state():
    """Initialize all required session state variables with default values."""
    defaults = AppConfig.get_default_session_state()
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value